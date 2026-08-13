import json
import time;
from openai import OpenAI;
from langgraph.graph import END, START, StateGraph;

from src.app.agents.state import AgentState
from src.app.core.config import settings
from src.app.services.tool_service import execute_tool
from src.app.services.conversation_service import save_tool_call
import time;

from src.app.services.refund_services import(
    update_refund_status,
)

client = OpenAI(
    api_key=settings.openai_api_key,
    timeout=20.0,
    max_retries=2,
)

from langgraph.types import interrupt;

# This is the description of the tools that we give to model , when to use.
tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the current status of a customer's order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, for example ORD-1001",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
  {
    "type": "function",
    "name": "create_support_ticket",
    "description": "Create a support ticket related to a customer's order.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID, for example CUST-001",
            },
            "order_id": {
                "type": "string",
                "description": "Order ID, for example ORD-1001",
            },
            "issue": {
                "type": "string",
                "description": "Description of the customer's problem",
            },
        },
        "required": [
            "customer_id",
            "order_id",
            "issue",
        ],
        "additionalProperties": False,
    },
    "strict": True,
},
{
    "type": "function",
    "name": "escalate_to_human",
    "description": "Escalate a customer's issue to a human support agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID, for example CUST-001",
            },
            "reason": {
                "type": "string",
                "description": "Reason why human support is needed",
            },
        },
        "required": ["customer_id", "reason"],
        "additionalProperties": False,
    },
    "strict": True,
},
{
    "type": "function",
    "name": "request_refund",
    "description": (
        "Create a pending refund request for a customer's order. "
        "This does not approve or complete the refund."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID, for example CUST-001",
            },
            "order_id": {
                "type": "string",
                "description": "Order ID, for example ORD-1001",
            },
            "reason": {
                "type": "string",
                "description": "Reason the customer is requesting a refund",
            },
        },
        "required": [
            "customer_id",
            "order_id",
            "reason",
        ],
        "additionalProperties": False,
    },
    "strict": True,
},
{
    "type": "function",
    "name": "search_knowledge_base",
    "description": (
        "Search the company knowledge base and documentation. "
        "Use this for questions about policies, instructions, "
        "product information, help documentation, or general "
        "company information."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "The user's question to search for "
                    "in the knowledge base."
                ),
            }
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

]


instructions = """
    You are a customer-support assistant for this company.

    Your job is to help customers using only:
    - the available tools
    - company information returned by search_knowledge_base
    - relevant information already available in the conversation

    Do not invent company policies, customer information, order information,
    tool results, actions, URLs, or capabilities.


    # ---------------------------------------------------------
    # ORDER STATUS
    # ---------------------------------------------------------

    Use get_order_status when the customer asks about:
    - an order status
    - delivery status
    - estimated delivery information available through the tool

    Never invent an order ID.

    If an order ID is required but missing, ask the customer for it.


    # ---------------------------------------------------------
    # SUPPORT TICKETS
    # ---------------------------------------------------------

    Use create_support_ticket when the customer explicitly wants
    a support ticket created.

    Never invent customer IDs or order IDs.

    Ask for any required information that is missing.


    # ---------------------------------------------------------
    # HUMAN ESCALATION
    # ---------------------------------------------------------

    Use escalate_to_human when:
    - the customer explicitly asks for a human
    - the issue cannot be handled with the available tools
    - escalation is clearly necessary

    Do not automatically escalate after a human refund rejection.

    If the customer wants escalation after a refund rejection,
    wait for the customer to explicitly request it in a new turn.


    # ---------------------------------------------------------
    # REFUNDS
    # ---------------------------------------------------------

    Use request_refund when the customer asks for a refund.

    The refund workflow works like this:

    1. request_refund initially creates a refund request with:
    status="pending_approval"

    2. The refund request is reviewed by a human.

    3. After human review, the latest refund result may contain:
    status="approved"
    OR
    status="rejected"
    OR
    status="pending_approval"

    Always use the LATEST refund status returned by the tool/workflow.

    If the latest status is "pending_approval":
    - Tell the customer that the refund request is waiting for human review.
    - Do not claim that it has been approved or completed.

    If the latest status is "approved":
    - Clearly tell the customer that the refund REQUEST was approved.
    - Do not describe it as still pending.
    - Do not claim that the refund payment itself has already been processed,
    transferred, credited, or completed unless a tool explicitly confirms that.

    If the latest status is "rejected":
    - Clearly tell the customer that the refund request was rejected
    by the human reviewer.
    - Do not automatically retry the refund.
    - Do not automatically create a support ticket.
    - Do not automatically escalate to a human.
    - Do not perform another action unless the customer explicitly asks
    for it in a new turn.

    An approved refund request does NOT automatically mean that money
    has already been returned to the customer.

    Never claim that a refund payment has been completed unless an
    available tool explicitly confirms completion.


    # ---------------------------------------------------------
    # COMPANY KNOWLEDGE / RAG
    # ---------------------------------------------------------

    Use search_knowledge_base for questions about:
    - company policies
    - returns
    - refunds
    - damaged items
    - delivery
    - cancellations
    - company instructions
    - product information
    - help documentation
    - other company information

    For company-information questions, you MUST use
    search_knowledge_base before answering.

    Do not answer company-information questions from your own
    general knowledge.

    When calling search_knowledge_base, make the search question
    self-contained using relevant conversation history.

    Resolve references such as:
    - "it"
    - "that item"
    - "that order"
    - "this product"
    - "they"

    when their meaning is clear from previous conversation messages.

    If search_knowledge_base returns found=true:
    - Base the answer on the returned documentation.
    - Summarize the relevant evidence.
    - Include the relevant source URL or URLs returned by the tool.
    - Never invent source URLs.

    If search_knowledge_base returns found=false:
    - Clearly tell the customer that the requested information
    was not found in the company knowledge base.
    - Do not fill the missing information using general knowledge.

    If search_knowledge_base already returned useful evidence during
    the current user turn, do not repeat the same search unnecessarily.


    # ---------------------------------------------------------
    # CONVERSATION HISTORY
    # ---------------------------------------------------------

    Use relevant information already available in the conversation.

    If a required customer ID, order ID, or other value was clearly
    provided earlier in the conversation, reuse it when appropriate.

    Do not invent missing identifiers.


    # ---------------------------------------------------------
    # AVAILABLE ACTIONS
    # ---------------------------------------------------------

    Only claim to perform actions supported by the available tools.

    Available capabilities include:
    - checking an order status
    - creating a support ticket
    - creating/requesting a refund
    - escalating to a human
    - searching company documentation

    Do not claim that you can:
    - arrange a replacement
    - modify an order
    - cancel an order unless a tool supports it
    - submit an external claim
    - upload files
    - attach files
    - receive or store photos
    - forward photos
    - add notes to an existing refund or case
    - update an existing ticket unless a tool supports it
    - provide tracking details that are not returned by a tool
    - send emails or notifications
    - perform payment actions

    unless an available tool explicitly supports that capability.


    # ---------------------------------------------------------
    # NOTIFICATIONS AND FUTURE ACTIONS
    # ---------------------------------------------------------

    Do not promise that the customer will receive:
    - an email
    - a message
    - a notification
    - an automatic update
    - future contact

    unless an available tool result or retrieved company documentation
    explicitly confirms that behavior.

    Do not say "I will notify you", "I'll pass this along",
    "I'll add this to the case", or similar statements unless a tool
    actually performed that action.


    # ---------------------------------------------------------
    # SCOPE
    # ---------------------------------------------------------

    For questions unrelated to this company or customer support,
    do not answer using general knowledge.

    Politely explain that you can only assist with company
    customer-support matters.


    # ---------------------------------------------------------
    # RESPONSE STYLE
    # ---------------------------------------------------------

    Keep responses concise, clear, and practical.

    For normal customer-support questions, generally stay within
    120-180 words unless the customer explicitly asks for more detail.

    Summarize documentation instead of copying long passages.

    When documentation contains many steps, provide only the most
    relevant next actions unless the customer asks for full instructions.

    Do not repeat the same information multiple times.

    Clearly distinguish between:
    - pending
    - approved
    - rejected
    - completed

    Never describe one status as another.

    Always base the final answer on the latest tool results and
    human-review result available in the current workflow.
    """

# ask agent what to do next, either direct answer or use tools .
# Ask the agent what to do next:
# either answer directly or request one/more tools.
def agent_node(
    state: AgentState,
) -> dict:
    """
    Call the OpenAI Responses API.

    First model call:
        Send the normal user/conversation messages.

    Later model calls:
        Continue from previous_response_id and send
        only the new tool outputs.

    This avoids storing raw OpenAI response objects
    inside LangGraph checkpoints.
    """

    start = time.perf_counter()

    # -------------------------------------------------
    # CONTROL WHICH TOOLS THE MODEL CAN USE
    # -------------------------------------------------

    # By default, the model can use all available tools.
    available_tools = tools

    # If a human already rejected the refund action,
    # the next model call should only explain the result.
    #
    # We do not want the model to automatically:
    # - retry the refund
    # - create a ticket
    # - escalate
    # - perform another action
    if state.get("refund_tool_approved") is False:
        available_tools = []

    # Get the previous OpenAI response ID.
    # It will be None on the first model call.
    previous_response_id = state.get(
        "previous_response_id"
    )

    # -------------------------------------------------
    # FIRST OPENAI CALL
    # -------------------------------------------------
    if not previous_response_id:

        response = client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            tools=available_tools,
            input=state["messages"],
        )
    
    # -------------------------------------------------
    # CONTINUE EXISTING OPENAI RESPONSE
    # -------------------------------------------------
    else:

        # Continue the earlier OpenAI response.
        #
        # previous_response_id keeps the model context
        # without us storing raw response objects.
        response = client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            tools=available_tools,
            previous_response_id=previous_response_id,
            input=state.get(
                "model_input",
                [],
            ),
        )

    # Measure how long the OpenAI call took.
    elapsed = (
        time.perf_counter()
        - start
    )

    print(
        f"[AGENT] OpenAI call: "
        f"{elapsed:.2f}s"
    )

    # -------------------------------------------------
    # FIND TOOL CALLS
    # -------------------------------------------------

    # Extract any function/tool calls requested
    # by the model.
    function_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    print(
        "[AGENT] Requested tools:",
        [
            item.name
            for item in function_calls
        ],
    )

    # Convert OpenAI tool-call objects into
    # plain Python dictionaries.
    #
    # These are safe for LangGraph/PostgreSQL
    # checkpoint persistence.
    pending_tool_calls = [
        {
            "name": item.name,
            "arguments": item.arguments,
            "call_id": item.call_id,
        }
        for item in function_calls
    ]

    # -------------------------------------------------
    # UPDATE LANGGRAPH STATE
    # -------------------------------------------------

    result = {
        # Save only the OpenAI response ID.
        "previous_response_id": response.id,

        # Save tool calls requested by the model.
        "pending_tool_calls": (
            pending_tool_calls
        ),

        # Clear previous tool outputs after
        # OpenAI has consumed them.
        "model_input": [],
    }

    # If no tool calls remain,
    # we have the final assistant response.
    if not function_calls:
        # Save the final assistant response.
        result["final_response"] = (
            response.output_text
        )

        # The refund decision only belongs to
        # the current workflow turn.
        #
        # Reset it so a future user message
        # does not inherit the old approval/rejection.
        result["refund_tool_approved"] = None

    return result


def route_after_agent(
    state: AgentState,
):
    """
    Decide what happens after the AI responds.

    If the model requested one or more tools:
        -> tool_node

    If no tools were requested:
        -> END

    IMPORTANT:
    Refunds are NOT routed directly to
    refund_approval_node anymore.

    tool_node will detect the refund and
    send it through prepare_refund_node first.
    """

    # Get the tools requested by the model.
    pending_calls = state.get(
        "pending_tool_calls",
        [],
    )

    # No tools requested means the AI already
    # produced the final customer response.
    if not pending_calls:
        return END

    # ALL tool calls go through tool_node first.
    #
    # Normal tools execute there.
    # request_refund is deferred from tool_node
    # to prepare_refund_node.
    return "tool_node"


def tool_node(
    state: AgentState,
) -> dict:
    """
    Execute normal tools.

    Refund calls are NOT executed here.

    If request_refund is present, it is preserved
    so the dedicated refund workflow can handle it.
    """

    # Outputs from normal tools.
    tool_outputs = []

    # Refund calls that must be handled later.
    deferred_calls = []

    for call in state[
        "pending_tool_calls"
    ]:

        # -------------------------------------------------
        # REFUND
        # -------------------------------------------------
        if call["name"] == "request_refund":

            # Do not execute it here.
            #
            # Send it to prepare_refund_node instead.
            deferred_calls.append(call)

            continue

        # -------------------------------------------------
        # NORMAL TOOL
        # -------------------------------------------------

        arguments = json.loads(
            call["arguments"]
        )

        start = time.perf_counter()

        result = execute_tool(
            name=call["name"],
            arguments=arguments,
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        print(
            f"[TOOL] {call['name']}: "
            f"{elapsed:.2f}s"
        )

        # Save normal tool execution for auditing.
        save_tool_call(
            conversation_id=state[
                "conversation_id"
            ],
            tool_name=call["name"],
            arguments=json.dumps(
                arguments
            ),
            result=json.dumps(
                result
            ),
        )

        # Give the result back to OpenAI later.
        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": json.dumps(result),
            }
        )

    return {
        # Normal tool outputs.
        "model_input": tool_outputs,

        # Usually empty.
        #
        # If a refund was requested,
        # it remains here for the next node.
        "pending_tool_calls": deferred_calls,
    }

def prepare_refund_node(
    state: AgentState,
) -> dict:
    """
    Create the refund request BEFORE human review.

    The database row is created with:

        status = pending_approval

    IMPORTANT:
    This node does NOT contain interrupt().

    The interrupt is in the next node.
    """

    # We expect the remaining tool call
    # to be request_refund.
    refund_call = next(
        call
        for call in state[
            "pending_tool_calls"
        ]
        if call["name"]
        == "request_refund"
    )

    # Convert the model arguments into Python data.
    arguments = json.loads(
        refund_call["arguments"]
    )

    # Use the existing tool.
    #
    # Your current request_refund already:
    # - validates customer/order
    # - creates the refund row
    # - sets status=pending_approval
    result = execute_tool(
        name="request_refund",
        arguments=arguments,
    )

    print(
        "[REFUND PREPARED]:",
        result,
    )

    # Save this tool execution for auditing.
    save_tool_call(
        conversation_id=state[
            "conversation_id"
        ],
        tool_name="request_refund",
        arguments=json.dumps(
            arguments
        ),
        result=json.dumps(
            result
        ),
    )

    # -------------------------------------------------
    # TOOL FAILED
    # -------------------------------------------------

    if "error" in result:

        # If creating the refund failed,
        # return the error to OpenAI.
        existing_outputs = list(
            state.get(
                "model_input",
                [],
            )
        )

        existing_outputs.append(
            {
                "type": "function_call_output",
                "call_id": refund_call[
                    "call_id"
                ],
                "output": json.dumps(
                    result
                ),
            }
        )

        return {
            "refund_request": None,
            "model_input": existing_outputs,
            "pending_tool_calls": [],
        }

    # -------------------------------------------------
    # SUCCESS
    # -------------------------------------------------

    # Save the pending refund information
    # into LangGraph state.
    return {
        "refund_request": result,
    }


def route_after_refund_prepare(
    state: AgentState,
):
    """
    Failed refund creation:
        go back to the agent.

    Successful pending refund:
        wait for human review.
    """

    if state.get(
        "refund_request"
    ) is None:
        return "agent_node"

    return "refund_approval_node"

def refund_approval_node(
    state: AgentState,
) -> dict:
    """
    Pause execution while a human reviews
    the already-created pending refund.
    """

    refund = state[
        "refund_request"
    ]

    # -------------------------------------------------
    # PAUSE HERE
    # -------------------------------------------------

    human_decision = interrupt(
        {
            "type": "refund_approval",

            "message": (
                "Review this pending "
                "refund request."
            ),

            "refund_id": refund.get(
                "refund_id"
            ),

            "customer_id": refund.get(
                "customer_id"
            ),

            "order_id": refund.get(
                "order_id"
            ),

            "reason": refund.get(
                "reason"
            ),

            "current_status": (
                "pending_approval"
            ),
        }
    )

    # Human sends:
    #
    # {"approved": True}
    #
    # or
    #
    # {"approved": False}
    approved = bool(
        human_decision.get(
            "approved",
            False,
        )
    )

    return {
        "refund_tool_approved": approved,
    }

def refund_decision_node(
    state: AgentState,
) -> dict:
    """
    Apply the human decision to the existing
    pending refund request.

    This node updates the database only.

    It does NOT ask OpenAI to generate the final
    transactional response.
    """

    # Get the pending refund that was created
    # before the human-review interrupt.
    refund = state[
        "refund_request"
    ]

    # Convert the human boolean decision
    # into our database status.
    if state.get(
        "refund_tool_approved"
    ) is True:

        new_status = "approved"

    else:

        new_status = "rejected"

    # Update the SAME refund database row.
    result = update_refund_status(
        refund_id=refund[
            "refund_id"
        ],
        new_status=new_status,
    )

    print(
        "[REFUND REVIEW RESULT]:",
        result,
    )


    # Save the final database result in graph state.
    #
    # The next node will use this directly
    # instead of asking the LLM to interpret it.
    return {
        "refund_review_result": result,

        # The original tool call is now finished.
        "pending_tool_calls": [],

        # We no longer need model tool outputs
        # for this refund workflow.
        "model_input": [],
    }


def refund_response_node(
    state: AgentState,
) -> dict:
    """
    Create the final refund response using
    deterministic Python code.

    We do this instead of asking the LLM because
    approved/rejected financial statuses should
    be communicated exactly as stored in the database.
    """

    result = state.get(
        "refund_review_result"
    )

    # ---------------------------------------------
    # SAFETY: RESULT MISSING
    # ---------------------------------------------

    if not result:

        final_response = (
            "The refund review finished, but the "
            "final refund status could not be loaded."
        )

    # ---------------------------------------------
    # SAFETY: DATABASE/SERVICE ERROR
    # ---------------------------------------------

    elif "error" in result:

        final_response = (
            "The refund review could not be completed. "
            f"Reason: {result['error']}"
        )

    else:

        # Read only trusted values returned
        # from our database/service.
        refund_id = result.get(
            "refund_id"
        )

        order_id = result.get(
            "order_id"
        )

        status = result.get(
            "status"
        )

        # -----------------------------------------
        # HUMAN APPROVED
        # -----------------------------------------

        if status == "approved":

            final_response = (
                "Your refund request has been approved.\n\n"
                f"Refund ID: {refund_id}\n"
                f"Order ID: {order_id}\n"
                "Status: Approved\n\n"
                "The refund request has passed human review. "
                "This does not confirm that the refund payment "
                "itself has already been completed."
            )

        # -----------------------------------------
        # HUMAN REJECTED
        # -----------------------------------------

        elif status == "rejected":

            final_response = (
                "Your refund request was rejected by "
                "the human reviewer.\n\n"
                f"Refund ID: {refund_id}\n"
                f"Order ID: {order_id}\n"
                "Status: Rejected\n\n"
                "No additional action was taken automatically."
            )

        # -----------------------------------------
        # UNEXPECTED STATUS
        # -----------------------------------------

        else:

            final_response = (
                "The refund review has finished.\n\n"
                f"Refund ID: {refund_id}\n"
                f"Order ID: {order_id}\n"
                f"Status: {status}"
            )

    # -------------------------------------------------
    # CLEAN TEMPORARY REFUND STATE
    # -------------------------------------------------

    return {
        # This is now the final response returned
        # by the LangGraph workflow.
        "final_response": final_response,

        # Human decision belonged only to this refund.
        "refund_tool_approved": None,

        # Temporary refund workflow data is finished.
        "refund_request": None,
        "refund_review_result": None,

        # We deliberately stop chaining the old
        # OpenAI response after this transactional flow.
        "previous_response_id": None,

        "pending_tool_calls": [],
        "model_input": [],
    }

def route_after_tool(
    state: AgentState,
):
    """
    Decide what happens after normal tools execute.

    If a refund call remains:
        prepare the pending refund.

    Otherwise:
        return tool results to OpenAI.
    """

    if state.get(
        "pending_tool_calls"
    ):
        return "prepare_refund_node"

    return "agent_node"

# ---------------------------------------------------------
# BUILD THE LANGGRAPH
# ---------------------------------------------------------

# Create a graph whose shared state is AgentState.
builder = StateGraph(AgentState)


# ---------------------------------------------------------
# REGISTER NODES
# ---------------------------------------------------------

# Main AI/model node.
# This decides whether to answer directly
# or request one or more tools.
builder.add_node(
    "agent_node",
    agent_node,
)


# Executes normal tools such as:
# get_order_status
# create_support_ticket
# escalate_to_human
# search_knowledge_base
#
# Refund calls are deferred to the special refund workflow.
builder.add_node(
    "tool_node",
    tool_node,
)


# Creates the refund request in PostgreSQL
# with status = pending_approval.
builder.add_node(
    "prepare_refund_node",
    prepare_refund_node,
)


# Pauses the graph using interrupt()
# and waits for human approval/rejection.
builder.add_node(
    "refund_approval_node",
    refund_approval_node,
)


# After the human decision,
# updates the SAME refund row to:
#
# approved
# OR
# rejected
builder.add_node(
    "refund_decision_node",
    refund_decision_node,
)

# Creates the final approved/rejected
# refund response without another LLM call.
builder.add_node(
    "refund_response_node",
    refund_response_node,
)


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

# Every new graph execution begins with the AI agent.
builder.add_edge(
    START,
    "agent_node",
)


# ---------------------------------------------------------
# AFTER AGENT NODE
# ---------------------------------------------------------

# route_after_agent decides:
#
# If tools were requested:
#     -> tool_node
#
# If no tools were requested:
#     -> END
builder.add_conditional_edges(
    "agent_node",
    route_after_agent,
)


# ---------------------------------------------------------
# AFTER TOOL NODE
# ---------------------------------------------------------

# route_after_tool decides:
#
# If request_refund is still pending:
#     -> prepare_refund_node
#
# Otherwise:
#     -> agent_node
#
# This is important because normal tools can finish
# immediately, while refunds require human review.
builder.add_conditional_edges(
    "tool_node",
    route_after_tool,
)


# ---------------------------------------------------------
# AFTER REFUND IS CREATED
# ---------------------------------------------------------

# route_after_refund_prepare decides:
#
# If refund creation failed:
#     -> agent_node
#
# If refund was successfully created:
#     -> refund_approval_node
builder.add_conditional_edges(
    "prepare_refund_node",
    route_after_refund_prepare,
)


# ---------------------------------------------------------
# HUMAN APPROVAL / REJECTION
# ---------------------------------------------------------

# When the human resumes the graph,
# continue to the node that updates the refund status.
builder.add_edge(
    "refund_approval_node",
    "refund_decision_node",
)


# After updating the database,
# create the deterministic final response.
builder.add_edge(
    "refund_decision_node",
    "refund_response_node",
)


# The deterministic refund response
# finishes this workflow.
builder.add_edge(
    "refund_response_node",
    END,
)


# ---------------------------------------------------------
# COMPILE GRAPH
# ---------------------------------------------------------

def build_agent_graph(
    checkpointer=None,
):
    """
    Compile the graph.

    A PostgreSQL checkpointer can be supplied
    so LangGraph can persist state and resume
    interrupted workflows.
    """

    return builder.compile(
        checkpointer=checkpointer,
    )


# Default compiled graph.
#
# Our checkpoint test / production code can instead call:
#
# build_agent_graph(checkpointer=checkpointer)
agent_graph = build_agent_graph()