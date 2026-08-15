
# --------------------------------------
# This code is running for runnning the agent manually without langgraph workflow,
# from fastapi import APIRouter, HTTPException
# from openai import OpenAIError

# from src.app.schemas.chat import ChatRequest, ChatResponse
# from src.app.services.ai_service import generate_ai_reply
# from src.app.services.conversation_service import (
#     conversation_exists,
#     create_conversation,
#     save_message,
# )


# router = APIRouter(prefix="/chat", tags=["Chat"])


# @router.post("", response_model=ChatResponse)
# def chat(request: ChatRequest) -> ChatResponse:

#     conversation_id = request.conversation_id

#     if conversation_id is None:
#         conversation_id = create_conversation()

#     elif not conversation_exists(conversation_id):
#         raise HTTPException(
#             status_code=404,
#             detail="Conversation not found.",
#         )

#     save_message(
#         conversation_id=conversation_id,
#         role="user",
#         content=request.message,
#     )

#     try:
#         reply = generate_ai_reply(
#             message=request.message,
#             conversation_id=conversation_id,
#         )

#         save_message(
#             conversation_id=conversation_id,
#             role="assistant",
#             content=reply,
#         )

#         return ChatResponse(
#             conversation_id=conversation_id,
#             reply=reply,
#         )

#     except OpenAIError:
#         raise HTTPException(
#             status_code=503,
#             detail="The AI service is currently unavailable.",
#         )




from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from src.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from src.app.services.agent_service import (
    get_pending_refund_review,
    run_agent_turn,
)

# IMPORTANT:
# /chat now uses our LangGraph agent instead
# of the old manual generate_ai_reply() loop.
from src.app.services.agent_service import (
    run_agent_turn,
)

from src.app.services.conversation_service import (
    conversation_exists,
    create_conversation,
    save_message,
)

from src.app.services.agent_service import (
    get_pending_refund_review,
    run_agent_turn,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Run one customer-support message through
    the production LangGraph workflow.
    """

    # -------------------------------------------------
    # CONVERSATION ID
    # -------------------------------------------------

    conversation_id = (
        request.conversation_id
    )

    # No conversation ID means this is
    # a new customer conversation.
    if conversation_id is None:
        conversation_id = (
            create_conversation()
        )

    # If a conversation ID was provided,
    # make sure it really exists.
    elif not conversation_exists(
        conversation_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )
    # -------------------------------------------------
    # CHECK FOR PENDING HUMAN REVIEW
    # -------------------------------------------------

    pending_refund = get_pending_refund_review(
        conversation_id=conversation_id,
    )

    if pending_refund:

        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "This conversation has a refund "
                    "waiting for human review."
                ),
                "refund_id": pending_refund.get(
                    "refund_id"
                ),
                "status": "pending_approval",
            },
        )

    # -------------------------------------------------
    # SAVE USER MESSAGE
    # -------------------------------------------------

    # Save the user message BEFORE running
    # LangGraph.
    #
    # agent_service.py will load conversation
    # history from PostgreSQL, including this
    # newest message.

    # -------------------------------------------------
    # CHECK FOR PENDING HUMAN REVIEW
    # -------------------------------------------------

    pending_refund = get_pending_refund_review(
        conversation_id=conversation_id,
    )

    if pending_refund:

        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "This conversation has a refund "
                    "waiting for human review."
                ),
                "refund_id": pending_refund.get(
                    "refund_id"
                ),
                "status": "pending_approval",
            },
        )
    save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    try:

        # -------------------------------------------------
        # RUN LANGGRAPH
        # -------------------------------------------------

        result = run_agent_turn(
            conversation_id=conversation_id,
        )

        # -------------------------------------------------
        # CHECK FOR HUMAN-IN-THE-LOOP INTERRUPT
        # -------------------------------------------------

        # With the current LangGraph invoke format,
        # an interrupted graph exposes the interrupt
        # information under "__interrupt__".
        interrupts = result.get(
            "__interrupt__",
            [],
        )

        if interrupts:

            # Our current refund flow creates one
            # interrupt at a time.
            interrupt_data = (
                interrupts[0].value
            )

            # ---------------------------------------------
            # REFUND APPROVAL REQUIRED
            # ---------------------------------------------

            if (
                isinstance(
                    interrupt_data,
                    dict,
                )
                and interrupt_data.get(
                    "type"
                )
                == "refund_approval"
            ):

                refund_id = (
                    interrupt_data.get(
                        "refund_id"
                    )
                )

                # This is a deterministic API response.
                #
                # We do NOT call OpenAI again because
                # the graph is currently paused waiting
                # for a human decision.
                reply = (
                    "Your refund request has been created "
                    "and is waiting for human review.\n\n"
                    f"Refund ID: {refund_id}\n"
                    "Status: Pending approval"
                )

                # Save exactly what the customer sees.
                save_message(
                    conversation_id=(
                        conversation_id
                    ),
                    role="assistant",
                    content=reply,
                )

                return ChatResponse(
                    conversation_id=conversation_id,
                    reply=reply,
                    status="pending_human_review",
                    requires_human_review=True,
                    data={},
                )

            # Safety fallback in case another type
            # of interrupt is added later.
            raise HTTPException(
                status_code=409,
                detail=(
                    "The workflow is waiting "
                    "for human input."
                ),
            )

        # -------------------------------------------------
        # NORMAL COMPLETED RESPONSE
        # -------------------------------------------------

        reply = result.get(
            "final_response"
        )

        # A completed graph should always have
        # a final response.
        if not reply:
            raise HTTPException(
                status_code=500,
                detail=(
                    "The agent completed without "
                    "producing a response."
                ),
            )

        # Save the final LangGraph response
        # into our normal messages table.
        save_message(
            conversation_id=(
                conversation_id
            ),
            role="assistant",
            content=reply,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,

            # LangGraph finished normally.
            status="completed",

            requires_human_review=False,

            data={},
        )

   
    # OPENAI FAILURE


    except OpenAIError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is currently "
                "unavailable."
            ),
        )