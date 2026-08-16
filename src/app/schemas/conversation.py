from datetime import datetime

from pydantic import BaseModel


class ConversationListItem(BaseModel):
    conversation_id: str
    title: str
    updated_at: datetime | None = None


class ConversationMessage(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ConversationMessagesResponse(BaseModel):
    conversation_id: str
    messages: list[ConversationMessage]