from typing import Dict, Tuple

from mcp import ClientSession


ToolRegistry = Dict[str, Tuple[ClientSession, str, dict]]


async def build_allowed_tool_registry(sessions, allowed_refs) -> ToolRegistry:
    tool_registry: ToolRegistry = {}

    for server_name, session in sessions.items():
        tools = await session.list_tools()
        for tool in tools.tools:
            full_ref = f"{server_name}/{tool.name}"
            if full_ref in allowed_refs:
                tool_registry[full_ref] = (session, tool.name, tool.inputSchema)

    return tool_registry


def get_tool_descriptions(tool_registry: ToolRegistry):
    return [
        {"name": full_ref, "schema": schema}
        for full_ref, (_, _, schema) in tool_registry.items()
    ]


def validate_tool_choice(agent_name: str, full_ref: str, tool_registry: ToolRegistry):
    if full_ref not in tool_registry:
        return {
            "error": f"Tool not allowed for {agent_name}: {full_ref}",
            "allowed_tools": sorted(tool_registry.keys()),
        }
    return None


async def call_registered_tool(tool_registry: ToolRegistry, full_ref: str, args: dict):
    session, tool_name, _ = tool_registry[full_ref]
    return await session.call_tool(tool_name, args)
