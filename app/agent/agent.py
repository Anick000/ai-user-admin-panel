import json
import os
import re
from groq import Groq
from mcp import ClientSession
from mcp.client.sse import sse_client

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class UserAgent:

    async def run(self, prompt: str):

        async with sse_client("http://127.0.0.1:8001/sse") as streams:
            async with ClientSession(*streams) as session:

                await session.initialize()

                # ---------------------------
                # Load MCP tools
                # ---------------------------
                tools = await session.list_tools()

                tool_descriptions = [
                    {
                        "name": t.name,
                        "schema": t.inputSchema
                    }
                    for t in tools.tools
                ]

                tool_names = [t.name for t in tools.tools]

                # ---------------------------
                # System prompt for LLM
                # ---------------------------
                system_prompt = f"""
You are an AI agent that manages users.

Available tools:
{tool_descriptions}

Rules:
- Return ONLY valid JSON
- No explanations
- No comments
- Never guess user_id
- For update or delete ALWAYS use the user's name
- The system will automatically resolve name → user_id

Examples:

Update:
{{
 "tool": "update_user_tool",
 "arguments": {{
  "name": "Rahul",
  "email": "rahul123@gmail.com"
 }}
}}

Delete:
{{
 "tool": "delete_user_tool",
 "arguments": {{
  "name": "Rahul"
 }}
}}

Format:

{{
 "tool": "tool_name",
 "arguments": {{}}
}}
"""

                # ---------------------------
                # Call LLM
                # ---------------------------
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )

                text = response.choices[0].message.content.strip()

                print("LLM response:", text)

                # ---------------------------
                # Extract JSON from response
                # ---------------------------
                match = re.search(r"\{.*\}", text, re.DOTALL)

                if not match:
                    return {"error": f"No JSON found in LLM output: {text}"}

                json_text = match.group()

                # Remove JS-style comments
                json_text = re.sub(r"//.*", "", json_text)

                try:
                    tool_call = json.loads(json_text)
                except Exception:
                    return {"error": f"Invalid JSON from LLM: {text}"}

                tool = tool_call.get("tool")
                args = tool_call.get("arguments", {})

                # ---------------------------
                # Validate tool
                # ---------------------------
                if tool not in tool_names:
                    return {"error": f"Invalid tool requested: {tool}"}

                # ---------------------------
                # Fix incorrect user_id usage
                # Example:
                # "user_id": "Rahul"
                # ---------------------------
                if "user_id" in args and isinstance(args["user_id"], str):

                    if not re.match(r"[0-9a-f-]{36}", args["user_id"]):
                        args["name"] = args["user_id"]
                        args.pop("user_id")

                # ---------------------------
                # Resolve name → user_id
                # ---------------------------
                if tool in ["update_user_tool", "delete_user_tool"]:

                    if "user_id" not in args:

                        users = await session.call_tool("get_users_tool", {})

                        user_data = json.loads(users.content[0].text)

                        # normalize to list
                        if isinstance(user_data, dict):
                            user_data = [user_data]

                        target_name = args.get("name")

                        if not target_name:
                            return {"error": "User name not provided"}

                        target_name = target_name.lower()

                        user_id = None

                        for u in user_data:
                            if u["name"].lower() == target_name:
                                user_id = u["id"]
                                break

                        if not user_id:
                            return {"error": "User not found"}

                        args["user_id"] = user_id

                    # remove name because MCP tool expects user_id
                    args.pop("name", None)

                # ---------------------------
                # Execute tool
                # ---------------------------
                result = await session.call_tool(tool, args)

                return result