import uuid
from src.app.db.models.conversation import Conversation
from src.app.db.models.feedback import Feedback
from src.app.db.session import SessionLocal


def save_feedback(
    conversation_id: str,
    rating: int,
    comment: str | None,
) -> dict:

    with SessionLocal() as db:

        conversation = db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            return {
                "error": "Conversation not found"
            }

        feedback_id = f"FDB-{uuid.uuid4().hex[:8].upper()}"

        feedback = Feedback(
            id=feedback_id,
            conversation_id=conversation_id,
            rating=rating,
            comment=comment,
        )

        db.add(feedback)
        db.commit()

        return {
            "feedback_id": feedback_id,
            "status": "saved",
        }