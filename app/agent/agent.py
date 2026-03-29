import json
import os
import re
from contextlib import AsyncExitStack
from typing import Dict, Tuple

from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession
from mcp.client.sse import sse_client

from app.agent.acl import AGENT_PERMISSIONS, MCP_SERVERS


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class MultiMCPAgent:
    def __init__(self, agent_name: str):
        if agent_name not in AGENT_PERMISSIONS:
            raise ValueError(f"Unknown agent: {agent_name}")

        self.agent_name = agent_name
        self.agent_config = AGENT_PERMISSIONS[agent_name]

    async def run(self, prompt: str):
        allowed_refs = set(self.agent_config["allowed_tools"])
        tool_registry: Dict[str, Tuple[ClientSession, str, dict]] = {}

        async with AsyncExitStack() as stack:
            sessions = {}

            for server_name, url in MCP_SERVERS.items():
                streams = await stack.enter_async_context(sse_client(url))
                session = await stack.enter_async_context(ClientSession(*streams))
                await session.initialize()
                sessions[server_name] = session

            for server_name, session in sessions.items():
                tools = await session.list_tools()
                for t in tools.tools:
                    full_ref = f"{server_name}/{t.name}"
                    if full_ref in allowed_refs:
                        tool_registry[full_ref] = (session, t.name, t.inputSchema)

            if not tool_registry:
                return {"error": f"No allowed tools configured for {self.agent_name}"}

            direct_tool, direct_args = self._try_direct_tool_choice(prompt, set(tool_registry.keys()))
            if direct_tool:
                session, tool_name, _ = tool_registry[direct_tool]
                result = await session.call_tool(tool_name, direct_args)
                parsed_result = self._parse_mcp_result(result)
                return {
                    "agent": self.agent_name,
                    "tool": direct_tool,
                    "result": parsed_result,
                }

            tool_descriptions = [
                {"name": full_ref, "schema": schema}
                for full_ref, (_, _, schema) in tool_registry.items()
            ]

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

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            text = response.choices[0].message.content.strip()
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return {"error": f"No JSON found in LLM output: {text}"}

            json_text = re.sub(r"//.*", "", match.group())

            try:
                tool_call = json.loads(json_text)
            except Exception:
                return {"error": f"Invalid JSON from LLM: {text}"}

            full_ref = tool_call.get("tool")
            args = tool_call.get("arguments", {})

            if full_ref not in tool_registry:
                return {
                    "error": f"Tool not allowed for {self.agent_name}: {full_ref}",
                    "allowed_tools": sorted(tool_registry.keys()),
                }

            session, tool_name, _ = tool_registry[full_ref]
            result = await session.call_tool(tool_name, args)
            parsed_result = self._parse_mcp_result(result)

            return {
                "agent": self.agent_name,
                "tool": full_ref,
                "result": parsed_result,
            }

    def _try_direct_tool_choice(self, prompt: str, available_tools: set):
        p = prompt.lower().strip()
        p_compact = re.sub(r"\s+", " ", p)

        all_users_phrases = [
            "all users",
            "all user",
            "show users",
            "show all",
            "list users",
            "get users",
            "users list",
            "all usera",
        ]
        if any(phrase in p_compact for phrase in all_users_phrases):
            if "mcp1/get_users_tool" in available_tools:
                return "mcp1/get_users_tool", {}

        if re.search(r"\b(show|list|get|display)\b.*\b(all )?users\b", p):
            if "mcp1/get_users_tool" in available_tools:
                return "mcp1/get_users_tool", {}

        if re.search(r"\b(count|total|how many)\b.*\busers?\b", p):
            if "mcp2/get_user_count_tool" in available_tools:
                return "mcp2/get_user_count_tool", {}

        if re.search(r"\b(latest|last)\b.*\buser\b", p):
            if "mcp2/get_latest_user_tool" in available_tools:
                return "mcp2/get_latest_user_tool", {}

        email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", prompt)
        if email_match and "mcp2/find_user_by_email_tool" in available_tools:
            return "mcp2/find_user_by_email_tool", {"email": email_match.group(1)}

        # Name-based lookup patterns:
        # "find user Rahul", "find user by name Rahul", "get user named Rahul"
        if "mcp2/find_user_by_name_tool" in available_tools:
            by_name_match = re.search(
                r"\b(?:find|get|search|lookup)\s+(?:for\s+)?user(?:\s+(?:by|with)\s+name)?\s+(?:named\s+)?([a-zA-Z][a-zA-Z .'-]{1,60})\b",
                prompt,
                re.IGNORECASE,
            )
            if by_name_match:
                name = by_name_match.group(1).strip()
                return "mcp2/find_user_by_name_tool", {"name": name}

            named_match = re.search(r"\buser\s+named\s+([a-zA-Z][a-zA-Z .'-]{1,60})\b", prompt, re.IGNORECASE)
            if named_match and not email_match:
                return "mcp2/find_user_by_name_tool", {"name": named_match.group(1).strip()}

        return None, None

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
