from src.app.db.models.ticket import Ticket
from src.app.db.session import SessionLocal
from src.app.tools.order_tools import get_order_status
from src.app.tools.support_tools import create_support_ticket


# ORDER STATUS - EXISTING ORDER


def test_get_existing_order_status():
    result = get_order_status(
        "ORD-9001"
    )

    assert result["found"] is True
    assert result["order_id"] == "ORD-9001"
    assert result["customer_id"] == "CUST-901"
    assert result["status"] == "shipped"

# ORDER STATUS - INVALID ORDER
def test_get_nonexistent_order_status():
    result = get_order_status(
        "ORD-DOES-NOT-EXIST"
    )

    assert result["found"] is False
    assert (
        result["order_id"]
        == "ORD-DOES-NOT-EXIST"
    )



# SUPPORT TICKET - SUCCESS
def test_create_support_ticket():
    """
    Create a real ticket using our test customer/order.
    The ticket is deleted afterward so repeated pytest
    runs do not fill the development database.
    """

    ticket_id = None

    try:
        result = create_support_ticket(
            customer_id="CUST-902",
            order_id="ORD-9004",
            issue=(
                "Automated pytest ticket test."
            ),
        )

        # Tool should return a real ticket.
        assert "error" not in result

        assert result["customer_id"] == "CUST-902"
        assert result["order_id"] == "ORD-9004"
        assert result["status"] == "open"

        ticket_id = result["ticket_id"]

        assert ticket_id.startswith(
            "TKT-"
        )

        # Verify that the ticket really exists
        # inside PostgreSQL.
        with SessionLocal() as db:
            ticket = db.get(
                Ticket,
                ticket_id,
            )

            assert ticket is not None
            assert ticket.customer_id == "CUST-902"
            assert ticket.order_id == "ORD-9004"
            assert ticket.status == "open"

    finally:

        # Clean up the ticket created by this test.
        if ticket_id is not None:

            with SessionLocal() as db:
                ticket = db.get(
                    Ticket,
                    ticket_id,
                )

                if ticket is not None:
                    db.delete(ticket)
                    db.commit()


# SUPPORT TICKET - WRONG CUSTOMER


def test_ticket_order_customer_mismatch():
    """
    ORD-9006 belongs to CUST-903.

    CUST-901 must not be allowed to create
    a ticket for that order.
    """

    result = create_support_ticket(
        customer_id="CUST-901",
        order_id="ORD-9006",
        issue="Ownership test.",
    )

    assert "error" in result

    assert result["error"] == (
        "This order does not belong "
        "to this customer."
    )