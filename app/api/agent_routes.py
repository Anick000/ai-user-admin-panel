from fastapi import APIRouter
from app.agent.acl import AGENT_PERMISSIONS
from app.agent.agent import MultiMCPAgent

router = APIRouter()


@router.post("/chat")
async def chat(prompt: str):
    # Backward compatible default route
    result = await MultiMCPAgent("agent1").run(prompt)
    return result


@router.get("/agents")
def list_agents():
    return {
        agent_name: {
            "description": cfg["description"],
            "allowed_tools": cfg["allowed_tools"],
        }
        for agent_name, cfg in AGENT_PERMISSIONS.items()
    }


@router.post("/agents/{agent_name}/chat")
async def chat_with_agent(agent_name: str, prompt: str):
    if agent_name not in AGENT_PERMISSIONS:
        return {
            "error": f"Unknown agent: {agent_name}",
            "available_agents": sorted(AGENT_PERMISSIONS.keys()),
        }

    result = await MultiMCPAgent(agent_name).run(prompt)
    return result
