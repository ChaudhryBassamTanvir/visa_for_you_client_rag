from fastapi import APIRouter
from services.ai_agent import handle_message

router = APIRouter()

@router.post("/")
async def chat(data: dict):
    user_message = data.get("message")
    response = handle_message(user_message)
    return {"response": response}