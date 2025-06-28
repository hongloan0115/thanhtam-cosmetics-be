from fastapi import APIRouter, Request
from app.core.openai_client import summarize_messages

router = APIRouter()

@router.post("/summary")
async def chat_summary(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    prev_summary = data.get("prev_summary")
    summary = summarize_messages(messages, prev_summary=prev_summary)
    return {"summary": summary}
