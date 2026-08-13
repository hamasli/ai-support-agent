from langgraph.checkpoint.postgres import PostgresSaver

from src.app.agents.agent_graph import build_agent_graph
from src.app.core.config import settings
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

    return result