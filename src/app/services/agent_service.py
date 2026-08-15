from langgraph.checkpoint.postgres import PostgresSaver

from src.app.agents.agent_graph import build_agent_graph
from src.app.core.config import settings
from langgraph.types import Command
from src.app.services.conversation_service import (
    get_conversation_messages,
)


# ---------------------------------------------------------
# LANGGRAPH POSTGRES DATABASE URL
# ---------------------------------------------------------

# SQLAlchemy uses:
#
# postgresql+psycopg://...
#
# LangGraph PostgresSaver expects:
#
# postgresql://...
checkpoint_db_url = str(
    settings.database_url
).replace(
    "postgresql+psycopg://",
    "postgresql://",
)


def get_pending_refund_review(
    conversation_id: str,
) -> dict | None:
    """
    Check whether this LangGraph conversation
    is currently paused waiting for human
    refund approval/rejection.
    """

    config = {
        "configurable": {
            "thread_id": conversation_id,
        }
    }

    with PostgresSaver.from_conn_string(
        checkpoint_db_url
    ) as checkpointer:

        agent_graph = build_agent_graph(
            checkpointer=checkpointer,
        )

        snapshot = agent_graph.get_state(
            config
        )

        # No saved state for this conversation.
        if not snapshot.values:
            return None

        pending_refund = snapshot.values.get(
            "refund_request"
        )

        # If refund_request still exists,
        # the refund workflow has not finished yet.
        if pending_refund:
            return pending_refund

    return None

def get_pending_refund_review(
    conversation_id: str,
) -> dict | None:
    """
    Check whether this LangGraph conversation
    currently has a refund waiting for
    human approval/rejection.
    """

    config = {
        "configurable": {
            "thread_id": conversation_id,
        }
    }

    with PostgresSaver.from_conn_string(
        checkpoint_db_url
    ) as checkpointer:

        checkpointer.setup()
        agent_graph = build_agent_graph(
            checkpointer=checkpointer,
        )
        

        

        snapshot = agent_graph.get_state(
            config
        )

        # No LangGraph state exists yet.
        if not snapshot.values:
            return None

        pending_refund = snapshot.values.get(
            "refund_request"
        )

        if pending_refund:
            return pending_refund

    return None



def run_agent_turn(
    conversation_id: str,
) -> dict:
    """
    Run one customer conversation turn through
    our real LangGraph support agent.

    The user message must already be saved in
    PostgreSQL before this function is called.
    """

    # -----------------------------------------------------
    # LOAD CONVERSATION HISTORY
    # -----------------------------------------------------

    # PostgreSQL remains our application-level
    # conversation history.
    #
    # This includes the latest user message because
    # /chat saves it before calling this function.
    messages = get_conversation_messages(
        conversation_id=conversation_id,
    )

    # -----------------------------------------------------
    # NEW USER-TURN STATE
    # -----------------------------------------------------

    state = {
        "conversation_id": conversation_id,

        # Give the model the current conversation history.
        "messages": messages,

        # Start a fresh OpenAI response chain for this
        # new user turn.
        #
        # Tool calls inside this same graph run may later
        # populate previous_response_id again.
        "previous_response_id": None,

        # Clear temporary tool state from a previous turn.
        "model_input": [],
        "pending_tool_calls": [],

        # Clear temporary refund/HITL state belonging
        # to an earlier completed turn.
        "refund_tool_approved": None,
        "refund_request": None,
        "refund_review_result": None,
         "final_response": "",
    }

    # -----------------------------------------------------
    # LANGGRAPH THREAD CONFIGURATION
    # -----------------------------------------------------

    # We use conversation_id as thread_id.
    #
    # Therefore:
    #
    # PostgreSQL conversation:
    # CONV-ABC123
    #
    # LangGraph thread:
    # CONV-ABC123
    #
    # Both refer to the same customer conversation.
    config = {
        "configurable": {
            "thread_id": conversation_id,
        },

        # Protect the graph from accidentally running
        # forever because of repeated tool calls.
        "recursion_limit": 10,
    }

    # -----------------------------------------------------
    # RUN THE GRAPH WITH POSTGRES CHECKPOINTING
    # -----------------------------------------------------

    # PostgresSaver persists LangGraph workflow state.
    #
    # This is especially important for refund approval:
    #
    # /chat
    #   ↓
    # interrupt()
    #   ↓
    # request ends
    #
    # Later:
    #
    # approval endpoint
    #   ↓
    # same thread_id
    #   ↓
    # Command(resume=...)
    with PostgresSaver.from_conn_string(
        checkpoint_db_url
    ) as checkpointer:

        # Safe to call while developing.
        # This ensures the LangGraph checkpoint
        # tables exist.
        checkpointer.setup()

        # Compile our real support graph with
        # persistent PostgreSQL checkpoints.
        agent_graph = build_agent_graph(
            checkpointer=checkpointer,
        )

        # Run this user turn.
        result = agent_graph.invoke(
            state,
            config=config,
        )
        # TEMPORARY DEBUG:
        # Show exactly what LangGraph returns when the
        # workflow pauses for human refund approval.
        print("\n================================")
        print("LANGGRAPH RESULT TYPE")
        print("================================")
        print(type(result))

        print("\n================================")
        print("LANGGRAPH RESULT")
        print("================================")
        print(result)

    return result

def resume_refund_review(
    conversation_id: str,
    refund_id: str,
    approved: bool,
) -> dict:
    """
    Resume a refund workflow that is paused
    waiting for human approval/rejection.

    Before resuming, verify that the refund ID
    belongs to the pending workflow.
    """

    config = {
        "configurable": {
            "thread_id": conversation_id,
        },
        "recursion_limit": 10,
    }

    with PostgresSaver.from_conn_string(
        checkpoint_db_url
    ) as checkpointer:

        checkpointer.setup()
        # Compile the graph using the same
        # persistent PostgreSQL checkpoints.
        agent_graph = build_agent_graph(
            checkpointer=checkpointer,
        )

        

        snapshot = agent_graph.get_state(
            config
        )

        pending_refund = snapshot.values.get(
            "refund_request"
        )

        # There must actually be a refund waiting
        # for human review in this conversation.
        if not pending_refund:
            raise ValueError(
                "No pending refund review was found "
                "for this conversation."
            )

        # Protect against someone submitting a refund ID
        # that belongs to another workflow.
        if (
            pending_refund.get("refund_id")
            != refund_id
        ):
            raise ValueError(
                "Refund ID does not match the pending "
                "refund for this conversation."
            )

        # -------------------------------------------------
        # RESUME interrupt()
        # -------------------------------------------------

        result = agent_graph.invoke(
            Command(
                resume={
                    "approved": approved,
                }
            ),
            config=config,
        )

    return result