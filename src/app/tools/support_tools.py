import uuid;

#is used to generate the unique IDs.


def create_support_ticket(
        customer_id:str,
        issue:str,
)->dict:

    ticket_id=f"TKT-{uuid.uuid4().hex[:6].upper()}"

    return {
        "ticket_id":ticket_id,
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