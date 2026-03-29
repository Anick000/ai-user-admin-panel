from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("User Insights MCP")

BASE_URL = "http://127.0.0.1:8000"


async def _get_all_users():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/users")
        return response.json()


@mcp.tool()
async def get_user_count_tool():
    users = await _get_all_users()
    return {"count": len(users)}

@mcp.tool()
async def find_user_by_email_tool(email: str):
    users = await _get_all_users()
    target_email = email.lower().strip()
    for user in users:
        if user.get("email", "").lower() == target_email:
            return user
    return {"error": "User not found"}


@mcp.tool()
async def find_user_by_name_tool(name: str):
    users = await _get_all_users()
    target_name = name.lower().strip()
    for user in users:
        if user.get("name", "").lower() == target_name:
            return user
    return {"error": "User not found"}


@mcp.tool()
async def get_latest_user_tool():
    users = await _get_all_users()
    if not users:
        return {"error": "No users found"}
    return users[-1]


app = mcp.sse_app()
