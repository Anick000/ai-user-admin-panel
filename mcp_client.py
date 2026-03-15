import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():

    # Connect to MCP server
    async with sse_client("http://127.0.0.1:8001/sse") as streams:

        async with ClientSession(*streams) as session:

            # Initialize session
            await session.initialize()

            print("Connected to MCP server")

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)

            # Call create user tool
            result = await session.call_tool(
                "create_user_tool",
                {
                    "name": "Rahul",
                    "email": "rahul@gmail.com"
                }
            )

            print("Create user result:", result)

            # Get all users
            users = await session.call_tool("get_users_tool", {})

            print("All users:", users)


asyncio.run(main())
