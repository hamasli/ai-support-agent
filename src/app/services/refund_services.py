from sqlalchemy import select

from src.app.db.models import RefundRequest
from src.app.db.session import SessionLocal


def update_refund_status(
    refund_id: str,
    new_status: str,
) -> dict:
    """
    Update a pending refund after human review.

    Allowed final decisions:
    - approved
    - rejected
    """

    # Only human-review statuses are accepted here.
    allowed_statuses = {
        "approved",
        "rejected",
    }

    if new_status not in allowed_statuses:
        return {
            "error": "Invalid refund status.",
        }

    # Open a database session.
    with SessionLocal() as db:

        # Find the refund request.
        refund = db.scalar(
            select(RefundRequest).where(
                RefundRequest.id == refund_id
            )
        )

        # Refund ID does not exist.
        if refund is None:
            return {
                "error": "Refund request not found.",
                "refund_id": refund_id,
            }
        # IDEMPOTENCY / SAFETY
        # Only pending refunds can receive a new decision.
        # If this function accidentally runs twice,
        # we do not change an already-reviewed request.
        if refund.status != "pending_approval":
            return {
                "refund_id": refund.id,
                "customer_id": refund.customer_id,
                "order_id": refund.order_id,
                "status": refund.status,
                "message": (
                    "This refund request has "
                    "already been reviewed."
                ),
            }

        # Apply the human decision.
        refund.status = new_status

        # Save it permanently.
        db.commit()

        # Reload database values.
        db.refresh(refund)

        return {
            "refund_id": refund.id,
            "customer_id": refund.customer_id,
            "order_id": refund.order_id,
            "status": refund.status,
        }