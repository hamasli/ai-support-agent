from fastapi import APIRouter, HTTPException


from src.app.schemas.feedback import (
    FeedbackRequest,
    FeedbackResponse,
)
from src.app.services.feedback_service import save_feedback
router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@router.post("", response_model=FeedbackResponse)
def create_feedback(
    request: FeedbackRequest,
) -> FeedbackResponse:

    result = save_feedback(
        conversation_id=request.conversation_id,
        rating=request.rating,
        comment=request.comment,
    )

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"],
        )

    return FeedbackResponse(**result)