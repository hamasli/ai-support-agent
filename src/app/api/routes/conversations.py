from fastapi import APIRouter, HTTPException

from src.app.schemas.conversation import (
    ConversationListItem,
    ConversationMessagesResponse,
)
from src.app.services.conversation_service import (
    conversation_exists,
    get_conversation_messages_for_ui,
    list_conversations,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


# ---------------------------------------------------------
# LIST CONVERSATIONS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[ConversationListItem],
)
def get_conversations():
    """
    Used by the frontend conversation sidebar.
    """

    return list_conversations()


# ---------------------------------------------------------
# GET ONE CONVERSATION'S MESSAGES
# ---------------------------------------------------------

@router.get(
    "/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
)
def get_messages(
    conversation_id: str,
):
    """
    Used when the user opens an old conversation.
    """

    if not conversation_exists(
        conversation_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    messages = (
        get_conversation_messages_for_ui(
            conversation_id
        )
    )

    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        messages=messages,
    )