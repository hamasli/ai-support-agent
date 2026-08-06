from fastapi import APIRouter

from src.app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        reply=f"You said: {request.message}"
    )