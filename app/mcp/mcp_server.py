from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("User Management MCP")

BASE_URL = "http://127.0.0.1:8000"


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
async def update_user_tool(user_id: str, name: str = None, email: str = None):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/users/{user_id}",
            json={
                "name": name,
                "email": email
            }
        )
        return response.json()



@mcp.tool()
async def delete_user_tool(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/users/{user_id}"
        )
        return response.json()


app = mcp.sse_app()