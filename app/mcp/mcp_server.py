from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional

mcp = FastMCP("User Management MCP")

BASE_URL = "http://127.0.0.1:8000"


async def _resolve_user_id_by_name(name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/users")
        users = response.json()

    target = name.lower()
    for user in users:
        if user.get("name", "").lower() == target:
            return user["id"]
    return None


@mcp.tool()
async def create_user_tool(name: str, email: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/users",
            json={"name": name, "email": email}
        )
        return response.json()


@mcp.tool()
async def get_users_tool():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/users")
        return response.json()


@mcp.tool()
async def update_user_tool(
    user_id: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    target_name: Optional[str] = None,
):
    resolved_user_id = user_id
    if not resolved_user_id and target_name:
        resolved_user_id = await _resolve_user_id_by_name(target_name)

    if not resolved_user_id:
        return {"error": "Provide either user_id or target_name"}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/users/{resolved_user_id}",
            json={
                "name": name,
                "email": email
            }
        )
        return response.json()



@mcp.tool()
async def delete_user_tool(user_id: Optional[str] = None, target_name: Optional[str] = None):
    resolved_user_id = user_id
    if not resolved_user_id and target_name:
        resolved_user_id = await _resolve_user_id_by_name(target_name)

    if not resolved_user_id:
        return {"error": "Provide either user_id or target_name"}

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/users/{resolved_user_id}"
        )
        return response.json()


app = mcp.sse_app()
