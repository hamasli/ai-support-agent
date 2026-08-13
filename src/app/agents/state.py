from typing import Any
from typing_extensions import NotRequired, TypedDict


class AgentState(TypedDict):
    # Our application's conversation ID.
    conversation_id: str

    # User/conversation messages.
    messages: list[Any]

    previous_response_id:NotRequired[
        str |  None
    ]
    

    # Tool outputs that will be sent back to OpenAI.
    model_input: NotRequired[
        list[dict[str, Any]]
    ]

    # Tool calls requested by OpenAI.
    pending_tool_calls: NotRequired[
        list[dict[str, Any]]
    ]

    # Final text response.
    final_response: NotRequired[str]

    # Human refund decision.
    refund_tool_approved: NotRequired[
        bool | None
    ]

    # Information about the refund request that
    # was created with status=pending_approval.
    refund_request: NotRequired[
        dict[str, Any] | None
    ]

    refund_review_result: NotRequired[
    dict[str, Any] | None
    ]