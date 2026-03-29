# Multi-Agent + Multi-MCP User Admin Panel

This project now supports:
- Multiple MCP servers
- Multiple agents
- Tool-level access control per agent (ACL)

## Current architecture

- FastAPI backend: `http://127.0.0.1:8000`
- MCP Server 1 (User CRUD): `http://127.0.0.1:8001/sse`
- MCP Server 2 (User Insights): `http://127.0.0.1:8002/sse`
- Agents with restricted tool access in `app/agent/acl.py`

## Tool matrix

### MCP Server 1 (CRUD)
- `create_user_tool`
- `get_users_tool`
- `update_user_tool`
- `delete_user_tool`

### MCP Server 2 (Insights)
- `get_user_count_tool`
- `find_user_by_email_tool`
- `find_user_by_name_tool`
- `get_latest_user_tool`

## Agent permissions (security ACL)

- `agent1`
  - `mcp1/create_user_tool`
  - `mcp2/get_user_count_tool`

- `agent2`
  - `mcp1/get_users_tool`
  - `mcp2/find_user_by_email_tool`
  - `mcp2/find_user_by_name_tool`

- `agent3`
  - `mcp1/update_user_tool`
  - `mcp2/get_latest_user_tool`

Agents are hard-restricted. Even if the LLM requests another tool, execution is blocked by server-side validation.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

## Run all services

Open 3 terminals:

1. Start FastAPI backend:

```bash
python -m uvicorn app.main:app --port 8000 --reload
```

2. Start MCP Server 1:

```bash
python -m uvicorn app.mcp.mcp_server:app --port 8001 --reload
```

3. Start MCP Server 2:

```bash
python -m uvicorn app.mcp.mcp_server_2:app --port 8002 --reload
```

## API endpoints

- `GET /agents`  
  Lists agents and allowed tools.

- `POST /agents/{agent_name}/chat?prompt=...`  
  Runs a prompt through a specific agent.

- `POST /chat?prompt=...`  
  Backward-compatible route. Uses `agent1`.

## Examples

### Agent1 (allowed)
- `create user named Ravi with email ravi@example.com`
- `how many users are there`

### Agent1 (blocked)
- `show all users` (not in agent1 ACL)

### Agent2 (allowed)
- `show all users`
- `find user with email ravi@example.com`

### Agent3 (allowed)
- `update user Rahul email to rahul_new@example.com using target_name Rahul`
- `show latest user`

## How to add more servers/agents/tools

1. Add a new MCP server file under `app/mcp/` and expose `app = mcp.sse_app()`.
2. Add server URL in `MCP_SERVERS` (`app/agent/acl.py`).
3. Add tools in that MCP server with `@mcp.tool()`.
4. Add or update agent permission entries in `AGENT_PERMISSIONS`.
5. Restart backend + MCP servers.

## Security checklist

- Keep ACL in code (`app/agent/acl.py`) and review before deploy.
- Never rely only on prompt instructions; always enforce tool checks in runtime.
- Give each agent minimum required tools (principle of least privilege).
- Prefer read-only tools for support/reporting agents.
