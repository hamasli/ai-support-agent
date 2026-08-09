from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    conversation_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(
        default=None,
        max_length=500,
    )


class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str