import json
import os
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from mcp import ClientSession
from mcp.client.sse import sse_client
from app.agent.acl_store import get_agent_config, get_mcp_servers
from app.agent.langfuse_tracing import flush_langfuse, get_langfuse_callbacks
from app.agent.tool_access import (
    build_allowed_tool_registry,
    call_registered_tool,
    get_tool_descriptions,
    validate_tool_choice,
)


load_dotenv()

DEFAULT_MODEL = "llama-3.1-8b-instant"
TOOL_CHOICE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        ("human", "{prompt}"),
    ]
)


class MultiMCPAgent:
    def __init__(self, agent_name: str):
        agent_config = get_agent_config(agent_name)
        if agent_config is None:
            raise ValueError(f"Unknown agent: {agent_name}")

        self.agent_name = agent_name
        self.agent_config = agent_config
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", DEFAULT_MODEL),
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.tool_choice_chain = TOOL_CHOICE_PROMPT | self.llm | JsonOutputParser()

    async def run(self, prompt: str):
        allowed_refs = set(self.agent_config["allowed_tools"])
        mcp_servers = get_mcp_servers()

        async with AsyncExitStack() as stack:
            sessions = {}

            for server_name, url in mcp_servers.items():
                streams = await stack.enter_async_context(sse_client(url))
                session = await stack.enter_async_context(ClientSession(*streams))
                await session.initialize()
                sessions[server_name] = session

            tool_registry = await build_allowed_tool_registry(sessions, allowed_refs)

            if not tool_registry:
                return {"error": f"No allowed tools configured for {self.agent_name}"}

            tool_descriptions = get_tool_descriptions(tool_registry)

            system_prompt = f"""
You are {self.agent_name}.
Role: {self.agent_config["description"]}

You can ONLY call these tools:
{tool_descriptions}

Rules:
- Return ONLY valid JSON
- Do not include explanations
- JSON format:
{{
  "tool": "mcp_name/tool_name",
  "arguments": {{}}
}}
"""

            try:
                callbacks = get_langfuse_callbacks()
                invoke_config = {
                    "run_name": f"{self.agent_name}-tool-choice",
                    "tags": ["mcp-user-server", self.agent_name],
                    "metadata": {
                        "langfuse_session_id": self.agent_name,
                        "agent_name": self.agent_name,
                        "allowed_tools": sorted(tool_registry.keys()),
                    },
                }
                if callbacks:
                    invoke_config["callbacks"] = callbacks

                tool_call = await self.tool_choice_chain.ainvoke(
                    {
                        "system_prompt": system_prompt,
                        "prompt": prompt,
                    },
                    config=invoke_config,
                )
            except Exception as exc:
                return {"error": f"Invalid JSON from LangChain LLM output: {exc}"}
            finally:
                flush_langfuse()

            full_ref = tool_call.get("tool")
            args = tool_call.get("arguments", {})

            tool_error = validate_tool_choice(self.agent_name, full_ref, tool_registry)
            if tool_error:
                return tool_error

            result = await call_registered_tool(tool_registry, full_ref, args)
            parsed_result = self._parse_mcp_result(result)

            return {
                "agent": self.agent_name,
                "tool": full_ref,
                "result": parsed_result,
            }

    def _parse_mcp_result(self, result):
        if not result or not getattr(result, "content", None):
            return ""

        parsed_items = []
        for item in result.content:
            text = getattr(item, "text", None)
            if text is None:
                continue
            try:
                parsed_items.append(json.loads(text))
            except Exception:
                parsed_items.append(text)

        if not parsed_items:
            return ""

        if len(parsed_items) == 1:
            return parsed_items[0]

        # Flatten list payloads when a tool returns chunked list items.
        if all(isinstance(x, list) for x in parsed_items):
            flattened = []
            for chunk in parsed_items:
                flattened.extend(chunk)
            return flattened

        return parsed_items
