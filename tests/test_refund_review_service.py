from sqlalchemy import select

from src.app.db.models.order import Order
from src.app.db.models.refund_request import RefundRequest
from src.app.db.session import SessionLocal
from src.app.services.refund_services import (
    update_refund_status,
)
from src.app.tools.support_tools import (
    request_refund,
)


TEST_ORDER_ID = "ORD-TST-REVIEW"



# TEST DATA SETUP


def prepare_test_order():
    """
    Create a reusable order specifically
    for refund review pytest tests.
    """

    with SessionLocal() as db:

        # Remove refunds left by an interrupted test.
        refunds = db.scalars(
            select(RefundRequest).where(
                RefundRequest.order_id
                == TEST_ORDER_ID
            )
        ).all()

        for refund in refunds:
            db.delete(refund)

        order = db.get(
            Order,
            TEST_ORDER_ID,
        )

        if order is None:
            order = Order(
                id=TEST_ORDER_ID,
                customer_id="CUST-902",
                product_name="Pytest Review Product",
                status="delivered",
                estimated_delivery=None,
            )

            db.add(order)

        db.commit()


def cleanup_test_refunds():
    """
    Delete only refund rows.
    Keep the reusable pytest order.
    """

    with SessionLocal() as db:

        refunds = db.scalars(
            select(RefundRequest).where(
                RefundRequest.order_id
                == TEST_ORDER_ID
            )
        ).all()

        for refund in refunds:
            db.delete(refund)

        db.commit()


# ---------------------------------------------------------
# APPROVAL
# ---------------------------------------------------------

def test_pending_refund_can_be_approved():

    prepare_test_order()

    try:

        # Create refund in pending state.
        created = request_refund(
            customer_id="CUST-902",
            order_id=TEST_ORDER_ID,
            reason="Pytest approval test.",
        )

        refund_id = created["refund_id"]

        assert (
            created["status"]
            == "pending_approval"
        )

        # Human-review service approves it.
        result = update_refund_status(
            refund_id=refund_id,
            new_status="approved",
        )

        assert result["refund_id"] == refund_id
        assert result["status"] == "approved"

        # Confirm PostgreSQL was really updated.
        with SessionLocal() as db:

            refund = db.get(
                RefundRequest,
                refund_id,
            )

            assert refund is not None
            assert refund.status == "approved"

    finally:
        cleanup_test_refunds()


# ---------------------------------------------------------
# REJECTION
# ---------------------------------------------------------

def test_pending_refund_can_be_rejected():

    prepare_test_order()

    try:

        # Create refund in pending state.
        created = request_refund(
            customer_id="CUST-902",
            order_id=TEST_ORDER_ID,
            reason="Pytest rejection test.",
        )

        refund_id = created["refund_id"]

        assert (
            created["status"]
            == "pending_approval"
        )

        # Human-review service rejects it.
        result = update_refund_status(
            refund_id=refund_id,
            new_status="rejected",
        )

        assert result["refund_id"] == refund_id
        assert result["status"] == "rejected"

        # Confirm PostgreSQL was really updated.
        with SessionLocal() as db:

            refund = db.get(
                RefundRequest,
                refund_id,
            )

            assert refund is not None
            assert refund.status == "rejected"

    finally:
        cleanup_test_refunds()