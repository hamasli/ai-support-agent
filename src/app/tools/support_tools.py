import uuid;

#is used to generate the unique IDs.


def create_support_ticket(
        customer_id:str,
        order_id:str,
        issue:str,
)->dict:

    ticket_id=f"TKT-{uuid.uuid4().hex[:6].upper()}"

    return {
        "ticket_id":ticket_id,
        "order_id": order_id,
        "customer_id":customer_id,
        "issue": issue,
        "status":"open",
  }


def escalate_to_human(
        customer_id:str,
        reason:str,
)-> dict:
    return {
        "customer_id":customer_id,
        "reason":reason,
        "status":"escalated",
    }


def request_refund(
        customer_id:str,
        order_id:str,
        reason:str,
) ->dict:
    refund_id=f"REF-{uuid.uuid4().hex[:6].upper()}"
    return {
        "refund_id":refund_id,
        "customer_id":customer_id,
        "order_id":order_id,
        "reason":reason,
        "status":"pending_approval",
    }