# from fastapi import APIRouter,HTTPException;
# from openai import OpenAIError;

# from src.app.schemas.chat import ChatRequest, ChatResponse
# from src.app.services.ai_service import generate_ai_reply;

# router = APIRouter(prefix="/chat", tags=["Chat"])


# @router.post("", response_model=ChatResponse)
# def chat(request: ChatRequest) -> ChatResponse:
#     try:
#         reply=generate_ai_reply(request.message)
#         return ChatResponse( reply=reply);
#     except OpenAIError:
#         raise HTTPException(
#             status_code=503,
#             detail="The AI service is currently unavailable",
#              )

from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from src.app.schemas.chat import ChatRequest, ChatResponse
from src.app.services.ai_service import generate_ai_reply
from src.app.services.conversation_service import (
    conversation_exists,
    create_conversation,
    save_message,
)


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:

    conversation_id = request.conversation_id

    if conversation_id is None:
        conversation_id = create_conversation()

    elif not conversation_exists(conversation_id):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    try:
        reply = generate_ai_reply(
            message=request.message,
            conversation_id=conversation_id,
        )

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=reply,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,
        )

    except OpenAIError:
        raise HTTPException(
            status_code=503,
            detail="The AI service is currently unavailable.",
        )

