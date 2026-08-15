from typing import Any, Literal

from pydantic import BaseModel, Field


class RefundReviewRequest(BaseModel):
    """
    Human decision for a pending refund.
    """

    # LangGraph uses this conversation ID
    # as its persistent thread_id.
    conversation_id: str

    # True  -> approve
    # False -> reject
    approved: bool


class RefundReviewResponse(BaseModel):
    """
    Response returned after the human decision
    has been applied.
    """

    conversation_id: str
    refund_id: str
    reply: str

    # Human review has now finished.
    status: Literal["completed"]

    requires_human_review: bool

    # Structured refund information for frontend.
    data: dict[str, Any] = Field(
        default_factory=dict
    )