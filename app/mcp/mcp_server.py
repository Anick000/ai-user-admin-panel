from mcp.server.fastmcp import FastMCP
from app.services.user_service import (
    create_user,
    get_users,
    update_user,
    delete_user
)

mcp = FastMCP("User Management MCP")


@mcp.tool()
def create_user_tool(name: str, email: str):
    return create_user(name, email)


@mcp.tool()
def get_users_tool():
    return get_users()


@mcp.tool()
def update_user_tool(user_id: str, name: str = None, email: str = None):
    return update_user(user_id, name, email)


@mcp.tool()
def delete_user_tool(user_id: str):
    return delete_user(user_id)


app = mcp.sse_app()



