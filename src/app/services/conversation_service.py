# this file is storing the conversion between the user and the AI.

import uuid
from datetime import datetime
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

def list_conversations() -> list[dict]:
    """
    Return conversations for the frontend sidebar.

    The first user message is used as the
    conversation title.
    """

    with SessionLocal() as db:

        conversations = db.scalars(
            select(Conversation)
        ).all()

        result = []

        for conversation in conversations:

            # First user message = sidebar title
            first_message = db.scalar(
                select(Message)
                .where(
                    Message.conversation_id
                    == conversation.id,
                    Message.role == "user",
                )
                .order_by(
                    Message.created_at.asc()
                )
                .limit(1)
            )

            # Latest message = sorting/sidebar activity
            latest_message = db.scalar(
                select(Message)
                .where(
                    Message.conversation_id
                    == conversation.id
                )
                .order_by(
                    Message.created_at.desc()
                )
                .limit(1)
            )

            if first_message:
                title = first_message.content

                # Keep sidebar titles short.
                if len(title) > 45:
                    title = title[:45] + "..."
            else:
                title = "New conversation"

            result.append(
                {
                    "conversation_id":
                        conversation.id,

                    "title":
                        title,

                    "updated_at":
                        (
                            latest_message.created_at
                            if latest_message
                            else None
                        ),
                }
            )

        # Newest conversations first.
        result.sort(
            key=lambda item: (
                item["updated_at"]
                or datetime.min
            ),
            reverse=True,
        )

        return result


def get_conversation_messages_for_ui(
    conversation_id: str,
) -> list[dict]:
    """
    Return full conversation history
    for the frontend.
    """

    with SessionLocal() as db:

        messages = db.scalars(
            select(Message)
            .where(
                Message.conversation_id
                == conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
        ).all()

        return [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at":
                    message.created_at,
            }
            for message in messages
        ]