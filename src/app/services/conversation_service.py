# this file is storing the conversion between the user and the AI.

import uuid

from src.app.db.models.conversation import Conversation
from src.app.db.models.message import Message
from src.app.db.models.tool_call import ToolCall
from src.app.db.session import SessionLocal
from sqlalchemy import select;

def create_conversation() -> str:
    conversation_id = f"CONV-{uuid.uuid4().hex[:8].upper()}"

    with SessionLocal() as db:
        conversation = Conversation(
            id=conversation_id,
            customer_id=None,
        )

        db.add(conversation)
        db.commit()

    return conversation_id


def conversation_exists(conversation_id: str) -> bool:
    with SessionLocal() as db:
        return db.get(Conversation, conversation_id) is not None


def save_message(
    conversation_id: str,
    role: str,
    content: str,
) -> None:

    message = Message(
        id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    with SessionLocal() as db:
        db.add(message)
        db.commit()


def save_tool_call(
    conversation_id: str,
    tool_name: str,
    arguments: str,
    result: str,
) -> None:

    tool_call = ToolCall(
        id=f"CALL-{uuid.uuid4().hex[:8].upper()}",
        conversation_id=conversation_id,
        tool_name=tool_name,
        arguments=arguments,
        result=result,
    )

    with SessionLocal() as db:
        db.add(tool_call)
        db.commit()


# every time , with the same conversion id, adding the previous context of chat history.
def get_conversation_messages(
    conversation_id: str,
    limit: int = 20,
) -> list[dict[str, str]]:

    with SessionLocal() as db:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = list(db.scalars(statement).all())

    messages.reverse()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]