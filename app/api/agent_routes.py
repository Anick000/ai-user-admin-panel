from fastapi import APIRouter
from app.agent.agent import UserAgent

router = APIRouter()

agent = UserAgent()


@router.post("/chat")
async def chat(prompt: str):

    result = await agent.run(prompt)

    return result
