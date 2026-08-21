from fastapi import APIRouter, HTTPException

from src.app.schemas.refunds import (
    RefundReviewRequest,
    RefundReviewResponse,
)

from src.app.services.agent_service import (
    resume_refund_review,
)

from src.app.services.conversation_service import (
    conversation_exists,
    save_message,
)


router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"],
)


@router.post(
    "/{refund_id}/review",
    response_model=RefundReviewResponse,
)
def review_refund(
    refund_id: str,
    request: RefundReviewRequest,
) -> RefundReviewResponse:
    """
    Approve or reject a refund that is currently
    paused inside the LangGraph HITL workflow.
    """

    conversation_id = (
        request.conversation_id
    )

    
    # VALIDATE CONVERSATION
    if not conversation_exists(
        conversation_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    try:

        # RESUME LANGGRAPH
        result = resume_refund_review(
            conversation_id=conversation_id,
            refund_id=refund_id,
            approved=request.approved,
        )

    except ValueError as error:

        # Examples:
        #
        # - no refund is waiting for approval
        # - wrong refund ID for this conversation
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )

    
    # GET DETERMINISTIC FINAL RESPONSE
    reply = result.get(
        "final_response"
    )
    if not reply:
        raise HTTPException(
            status_code=500,
            detail=(
                "The refund review completed "
                "without producing a response."
            ),
        )    
    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
    )

    # Human decision has completed successfully.
    refund_status = (
        "approved"
        if request.approved
        else "rejected"
    )

    return RefundReviewResponse(
        conversation_id=conversation_id,
        refund_id=refund_id,
        reply=reply,
        status="completed",
        requires_human_review=False,
        data={
            "refund_id": refund_id,
            "refund_status": refund_status,
        },
    )