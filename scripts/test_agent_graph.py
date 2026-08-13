# LangGraph PostgreSQL checkpoint saver.
# It stores graph state so an interrupted workflow
# can be resumed later.
from langgraph.checkpoint.postgres import PostgresSaver

# Command is used to resume a paused LangGraph.
from langgraph.types import Command

# Build our real support-agent graph.
from src.app.agents.agent_graph import build_agent_graph

# Application settings containing DATABASE_URL.
from src.app.core.config import settings

# Creates a real conversation row in our database.
from src.app.services.conversation_service import (
    create_conversation,
)


# ---------------------------------------------------------
# DATABASE URL FOR LANGGRAPH
# ---------------------------------------------------------

# SQLAlchemy uses:
#
# postgresql+psycopg://...
#
# PostgresSaver uses:
#
# postgresql://...
checkpoint_db_url = str(
    settings.database_url
).replace(
    "postgresql+psycopg://",
    "postgresql://",
)


# ---------------------------------------------------------
# OPEN POSTGRES CHECKPOINTER
# ---------------------------------------------------------

with PostgresSaver.from_conn_string(
    checkpoint_db_url
) as checkpointer:

    # Ensure LangGraph checkpoint tables exist.
    checkpointer.setup()

    # Compile our graph with persistent checkpointing.
    agent_graph = build_agent_graph(
        checkpointer=checkpointer,
    )

    # Create a new conversation.
    #
    # We also use this same ID as LangGraph's thread_id.
    conversation_id = create_conversation()

    # -----------------------------------------------------
    # INITIAL USER REQUEST
    # -----------------------------------------------------

    state = {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": "user",
                "content": (
                    "I want a refund for ORD-1001. "
                    "My customer ID is CUST-001. "
                    "The item arrived damaged."
                ),
            }
        ],
    }

    # The thread_id connects all checkpoints
    # belonging to this workflow.
    config = {
        "configurable": {
            "thread_id": conversation_id,
        },
        "recursion_limit": 10,
    }

    # -----------------------------------------------------
    # FIRST RUN
    # -----------------------------------------------------
    #
    # Expected:
    #
    # OpenAI requests request_refund
    #        ↓
    # pending refund is created
    #        ↓
    # interrupt()
    #        ↓
    # graph pauses

    result = agent_graph.invoke(
        state,
        config=config,
    )

    print("\n================================")
    print("CONVERSATION")
    print("================================")

    print(conversation_id)

    print("\n================================")
    print("HUMAN REVIEW REQUIRED")
    print("================================")

    # LangGraph returns interrupt information
    # when the graph pauses.
    interrupts = result.get(
        "__interrupt__",
        [],
    )

    print(interrupts)

    # -----------------------------------------------------
    # HUMAN APPROVES
    # -----------------------------------------------------

    print("\n================================")
    print("HUMAN DECISION: Rejected")
    print("================================")

    # Resume the SAME graph/thread.
    #
    # The value below becomes the return value
    # of interrupt() inside refund_approval_node.
    resumed_result = agent_graph.invoke(
        Command(
            resume={
                "approved": False,
            }
        ),
        config=config,
    )

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    print("\n================================")
    print("FINAL RESPONSE")
    print("================================")

    print(
        resumed_result.get(
            "final_response"
        )
    )