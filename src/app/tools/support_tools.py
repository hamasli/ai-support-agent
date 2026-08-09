import uuid;

from src.app.db.models.customer import Customer
from src.app.db.models.order import Order
from src.app.db.models.ticket import Ticket
from src.app.db.session import SessionLocal

#database imports
from src.app.db.models.customer import Customer
from src.app.db.models.order import Order
from src.app.db.models.ticket import Ticket
from src.app.db.models.refund_request import RefundRequest
from src.app.db.models.escalation import Escalation
from src.app.db.session import SessionLocal



def create_support_ticket(
    customer_id: str,
    order_id: str,
    issue: str,
) -> dict:

    with SessionLocal() as db:

        customer = db.get(Customer, customer_id)

        if customer is None:
            return {
                "error": "Customer not found",
                "customer_id": customer_id,
            }

        order = db.get(Order, order_id)

        if order is None:
            return {
                "error": "Order not found",
                "order_id": order_id,
            }

        if order.customer_id != customer_id:
            return {
                "error": "This order does not belong to this customer."
            }

        ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"

        ticket = Ticket(
            id=ticket_id,
            customer_id=customer_id,
            order_id=order_id,
            issue=issue,
            status="open",
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return {
            "ticket_id": ticket.id,
            "customer_id": ticket.customer_id,
            "order_id": ticket.order_id,
            "issue": ticket.issue,
            "status": ticket.status,
        }


def escalate_to_human(
    customer_id: str,
    reason: str,
) -> dict:

    with SessionLocal() as db:

        customer = db.get(Customer, customer_id)

        if customer is None:
            return {
                "error": "Customer not found",
                "customer_id": customer_id,
            }

        escalation_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"

        escalation = Escalation(
            id=escalation_id,
            customer_id=customer_id,
            reason=reason,
            status="escalated",
        )

        db.add(escalation)
        db.commit()
        db.refresh(escalation)

        return {
            "escalation_id": escalation.id,
            "customer_id": escalation.customer_id,
            "reason": escalation.reason,
            "status": escalation.status,
        }

def request_refund(
    customer_id: str,
    order_id: str,
    reason: str,
) -> dict:

    with SessionLocal() as db:

        customer = db.get(Customer, customer_id)

        if customer is None:
            return {
                "error": "Customer not found",
                "customer_id": customer_id,
            }

        order = db.get(Order, order_id)

        if order is None:
            return {
                "error": "Order not found",
                "order_id": order_id,
            }

        if order.customer_id != customer_id:
            return {
                "error": "This order does not belong to this customer."
            }

        refund_id = f"REF-{uuid.uuid4().hex[:6].upper()}"

        refund = RefundRequest(
            id=refund_id,
            customer_id=customer_id,
            order_id=order_id,
            reason=reason,
            status="pending_approval",
        )

        db.add(refund)
        db.commit()
        db.refresh(refund)

        return {
            "refund_id": refund.id,
            "customer_id": refund.customer_id,
            "order_id": refund.order_id,
            "reason": refund.reason,
            "status": refund.status,
        }