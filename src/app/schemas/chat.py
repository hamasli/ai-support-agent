from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500,
    )

    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str

    # Overall workflow/API status.
    status: Literal[
        "completed",
        "pending_human_review",
    ]

    # Frontend can use this to show
    # review controls when necessary.
    requires_human_review: bool

    # Extra structured information.
    # Example:
    # {
    #     "refund_id": "REF-123",
    #     "order_id": "ORD-9002",
    #     "refund_status": "pending_approval"
    # }
    data: dict[str, Any] = Field(
        default_factory=dict
    )