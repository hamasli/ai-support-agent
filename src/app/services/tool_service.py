import json
import traceback;
from pydantic import ValidationError

from src.app.schemas.tool_schemas import (
    CreateTicketArgs,
    EscalateArgs,
    KnowledgeSearchArgs,
    OrderStatusArgs,
    RefundRequestArgs,
)
from src.app.tools.knowledge_tools import search_knowledge_base
from src.app.tools.order_tools import get_order_status
from src.app.tools.support_tools import (
    create_support_ticket,
    escalate_to_human,
    request_refund,
)


def execute_tool(
    name: str,
    arguments: dict,
    conversation_id: str | None = None,
) -> dict:

    try:

        if name == "get_order_status":
            args = OrderStatusArgs(**arguments)

            return get_order_status(
                args.order_id
            )

        if name == "create_support_ticket":
            args = CreateTicketArgs(**arguments)

            return create_support_ticket(
                customer_id=args.customer_id,
                order_id=args.order_id,
                issue=args.issue,
            )

        if name == "request_refund":
            args = RefundRequestArgs(**arguments)

            return request_refund(
                customer_id=args.customer_id,
                order_id=args.order_id,
                reason=args.reason,
                conversation_id=conversation_id,
            )

        if name == "escalate_to_human":
            args = EscalateArgs(**arguments)

            return escalate_to_human(
                customer_id=args.customer_id,
                reason=args.reason,
            )

        if name == "search_knowledge_base":
            args = KnowledgeSearchArgs(**arguments)

            return search_knowledge_base(
                question=args.question,
            )

        return {
            "error": f"Unknown tool: {name}"
        }

    except ValidationError as error:
        return {
            "error": "Invalid tool arguments",
            "details": error.errors(
                include_url=False
            ),
        }

    except Exception as error:

        print(
            f"\n[TOOL ERROR] {name}: "
            f"{type(error).__name__}: {error}"
        )

        traceback.print_exc()

        return {
            "error": "Tool execution failed",
            "details": (
                f"{type(error).__name__}: {error}"
            ),
        }