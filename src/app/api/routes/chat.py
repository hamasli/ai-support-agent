from fastapi import APIRouter,HTTPException;
from openai import OpenAIError;

from src.app.schemas.chat import ChatRequest, ChatResponse
from src.app.services.ai_service import generate_ai_reply;

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply=generate_ai_reply(request.message)
        return ChatResponse( reply=reply);
    except OpenAIError:
        raise HTTPException(
            status_code=503,
            detail="The AI service is currently unavailable",
             )