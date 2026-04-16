from fastapi import APIRouter
from app.agent.agent import MultiMCPAgent
from app.agent.acl_store import agent_exists, get_agent_permissions
from app.agent.langfuse_tracing import get_langfuse_status

router = APIRouter()


@router.post("/chat")
async def chat(prompt: str):
    # Backward compatible default route
    result = await MultiMCPAgent("agent1").run(prompt)
    return result


@router.get("/agents")
def list_agents():
    agent_permissions = get_agent_permissions()
    return {
        agent_name: {
            "description": cfg["description"],
            "allowed_tools": cfg["allowed_tools"],
        }
        for agent_name, cfg in agent_permissions.items()
    }


@router.get("/observability/langfuse")
def langfuse_observability_status():
    return get_langfuse_status()


@router.post("/agents/{agent_name}/chat")
async def chat_with_agent(agent_name: str, prompt: str):
    if not agent_exists(agent_name):
        return {
            "error": f"Unknown agent: {agent_name}",
            "available_agents": sorted(get_agent_permissions().keys()),
        }

    result = await MultiMCPAgent(agent_name).run(prompt)
    return result
