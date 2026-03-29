MCP_SERVERS = {
    "mcp1": "http://127.0.0.1:8001/sse",
    "mcp2": "http://127.0.0.1:8002/sse",
}


AGENT_PERMISSIONS = {
    "agent1": {
        "description": "Onboarding agent: can create users and view user count.",
        "allowed_tools": [
            "mcp1/create_user_tool",
            "mcp2/get_user_count_tool",
        ],
    },
    "agent2": {
        "description": "Support agent: can list users and find by email or name.",
        "allowed_tools": [
            "mcp1/get_users_tool",
            "mcp2/find_user_by_email_tool",
            "mcp2/find_user_by_name_tool",
        ],
    },
    "agent3": {
        "description": "Maintenance agent: can update users and inspect latest user.",
        "allowed_tools": [
            "mcp1/update_user_tool",
            "mcp2/get_latest_user_tool",
        ],
    },
}
