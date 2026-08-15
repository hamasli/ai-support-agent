from sqlalchemy import select

from src.app.db.models.escalation import Escalation
from src.app.db.models.order import Order
from src.app.db.models.refund_request import RefundRequest
from src.app.db.session import SessionLocal
from src.app.tools.support_tools import (
    escalate_to_human,
    request_refund,
)


# Dedicated order only for pytest.
# This prevents our automated tests from
# interfering with manual refund/HITL test data.
TEST_REFUND_ORDER_ID = "ORD-TST-REFUND"

# TEST DATA HELPERS


def prepare_refund_test_order():
    """
    Create/reset a dedicated test order.

    CUST-902 already exists in our seeded test data.
    """

    with SessionLocal() as db:

        # Remove leftover refund rows from an
        # earlier failed/interrupted pytest run.
        old_refunds = db.scalars(
            select(RefundRequest).where(
                RefundRequest.order_id
                == TEST_REFUND_ORDER_ID
            )
        ).all()

        for refund in old_refunds:
            db.delete(refund)

        order = db.get(
            Order,
            TEST_REFUND_ORDER_ID,
        )

        if order is None:
            order = Order(
                id=TEST_REFUND_ORDER_ID,
                customer_id="CUST-902",
                product_name="Pytest Refund Product",
                status="delivered",
                estimated_delivery=None,
            )

            db.add(order)

        db.commit()

def cleanup_refund_test_order():
    """
    Remove only refund rows created during tests.

    Keep ORD-TST-REFUND in the database because
    it is our reusable dedicated pytest order.
    """

    with SessionLocal() as db:

        refunds = db.scalars(
            select(RefundRequest).where(
                RefundRequest.order_id
                == TEST_REFUND_ORDER_ID
            )
        ).all()

        for refund in refunds:
            db.delete(refund)

        db.commit()


# ESCALATION - SUCCESS


def test_escalate_to_human():
    escalation_id = None

    try:
        result = escalate_to_human(
            customer_id="CUST-902",
            reason="Automated pytest escalation test.",
        )

        assert "error" not in result

        assert result["customer_id"] == "CUST-902"
        assert result["status"] == "escalated"

        escalation_id = result[
            "escalation_id"
        ]

        assert escalation_id.startswith(
            "ESC-"
        )

        # Confirm that the escalation was
        # actually saved in PostgreSQL.
        with SessionLocal() as db:

            escalation = db.get(
                Escalation,
                escalation_id,
            )

            assert escalation is not None
            assert (
                escalation.customer_id
                == "CUST-902"
            )
            assert (
                escalation.status
                == "escalated"
            )

    finally:

        # Remove test row afterward.
        if escalation_id is not None:

            with SessionLocal() as db:

                escalation = db.get(
                    Escalation,
                    escalation_id,
                )

                if escalation is not None:
                    db.delete(escalation)
                    db.commit()



# ESCALATION - INVALID CUSTOMER


def test_escalation_invalid_customer():

    result = escalate_to_human(
        customer_id="CUST-DOES-NOT-EXIST",
        reason="Test.",
    )

    assert "error" in result
    assert result["error"] == (
        "Customer not found"
    )


# ---------------------------------------------------------
# REFUND - CREATE
# ---------------------------------------------------------

def test_create_refund():

    prepare_refund_test_order()

    try:

        result = request_refund(
            customer_id="CUST-902",
            order_id=TEST_REFUND_ORDER_ID,
            reason="Automated pytest refund test.",
        )

        assert "error" not in result

        assert result["customer_id"] == "CUST-902"
        assert (
            result["order_id"]
            == TEST_REFUND_ORDER_ID
        )

        assert (
            result["status"]
            == "pending_approval"
        )

        assert result["created"] is True

        refund_id = result[
            "refund_id"
        ]

        assert refund_id.startswith(
            "REF-"
        )

        # Verify actual PostgreSQL row.
        with SessionLocal() as db:

            refund = db.get(
                RefundRequest,
                refund_id,
            )

            assert refund is not None

            assert (
                refund.status
                == "pending_approval"
            )

            assert (
                refund.order_id
                == TEST_REFUND_ORDER_ID
            )

    finally:
        cleanup_refund_test_order()


# ---------------------------------------------------------
# REFUND - DUPLICATE PROTECTION
# ---------------------------------------------------------

def test_duplicate_refund_is_prevented():

    prepare_refund_test_order()

    try:

        # First request should create a refund.
        first_result = request_refund(
            customer_id="CUST-902",
            order_id=TEST_REFUND_ORDER_ID,
            reason="First pytest refund request.",
        )

        assert first_result[
            "created"
        ] is True

        first_refund_id = first_result[
            "refund_id"
        ]

        # Same customer + same order should
        # NOT create another active refund.
        second_result = request_refund(
            customer_id="CUST-902",
            order_id=TEST_REFUND_ORDER_ID,
            reason="Duplicate pytest request.",
        )

        assert second_result[
            "created"
        ] is False

        # Must return the SAME refund.
        assert (
            second_result["refund_id"]
            == first_refund_id
        )

        assert (
            second_result["status"]
            == "pending_approval"
        )

        # Confirm PostgreSQL contains exactly
        # one refund for this test order.
        with SessionLocal() as db:

            refunds = db.scalars(
                select(RefundRequest).where(
                    RefundRequest.order_id
                    == TEST_REFUND_ORDER_ID
                )
            ).all()

            assert len(refunds) == 1

    finally:
        cleanup_refund_test_order()