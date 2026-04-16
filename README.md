# Multi-Agent + Multi-MCP User Admin Panel

This project now supports:
- Multiple MCP servers
- Multiple agents
- Tool-level access control per agent (ACL)
- Langfuse tracing for the LangChain agent decision step

## Current architecture

- FastAPI backend: `http://127.0.0.1:8000`
- MCP Server 1 (User CRUD): `http://127.0.0.1:8001/sse`
- MCP Server 2 (User Insights): `http://127.0.0.1:8002/sse`
- Agents with restricted tool access in `app/agent/acl.json`

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
  - `mcp1/delete_user_tool`
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
GROQ_MODEL=llama-3.1-8b-instant
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

`GROQ_MODEL` is optional. If omitted, the LangChain agent uses `llama-3.1-8b-instant`.

Langfuse is optional. If the Langfuse keys are missing, the app still runs, but traces are not sent.

Use `LANGFUSE_BASE_URL=https://cloud.langfuse.com` for the EU cloud region. If your Langfuse project is in the US region, use `LANGFUSE_BASE_URL=https://us.cloud.langfuse.com`.

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

- `GET /observability/langfuse`
  Shows whether Langfuse is installed, configured, and enabled.

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
- `delete user named Rahul`
- `show latest user`

## How to access Langfuse traces

1. Create a Langfuse account or open your self-hosted Langfuse instance.
2. Create a project in Langfuse.
3. Copy the project's public key and secret key into your `.env` file:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

4. Restart the FastAPI backend.
5. Send a chat request through the dashboard or API, for example:

```bash
curl -X POST "http://127.0.0.1:8000/agents/agent1/chat?prompt=how%20many%20users%20are%20there"
```

6. Open Langfuse in your browser:
   - EU cloud: `https://cloud.langfuse.com`
   - US cloud: `https://us.cloud.langfuse.com`
   - Self-hosted: your own Langfuse URL

7. Choose your project, then open the Traces page. You should see runs named like `agent1-tool-choice`, `agent2-tool-choice`, or `agent3-tool-choice`.

You can also check the local setup with:

```bash
curl http://127.0.0.1:8000/observability/langfuse
```

If it says `"enabled": false`, check that `langfuse` is installed and that both Langfuse keys are present in `.env`.

## How to add more servers/agents/tools

1. Add a new MCP server file under `app/mcp/` and expose `app = mcp.sse_app()`.
2. Add server URL in `mcp_servers` (`app/agent/acl.json`).
3. Add tools in that MCP server with `@mcp.tool()`.
4. Add or update agent permission entries in `agent_permissions`.
5. Restart backend + MCP servers.

## Security checklist

- Keep ACL in config (`app/agent/acl.json`) and review before deploy.
- Never rely only on prompt instructions; always enforce tool checks in runtime.
- Give each agent minimum required tools (principle of least privilege).
- Prefer read-only tools for support/reporting agents.
