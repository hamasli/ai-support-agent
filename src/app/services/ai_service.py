
import json
# this is used to saves the conversation, and the tools calls, and the messages.
from src.app.services.conversation_service import (
    get_conversation_messages,
    save_tool_call,
)
from openai import OpenAI
from pydantic import ValidationError

from src.app.core.config import settings
from src.app.tools.order_tools import get_order_status
from src.app.tools.support_tools import (
    create_support_ticket,
    escalate_to_human,
    request_refund,
    
)
from src.app.tools.knowledge_tools import search_knowledge_base
from src.app.schemas.tool_schemas import (
    OrderStatusArgs,
    CreateTicketArgs,
    EscalateArgs,
    RefundRequestArgs,
    KnowledgeSearchArgs
)
from src.app.services.tool_service import execute_tool

client = OpenAI(
    api_key=settings.openai_api_key,
    timeout=20.0,
    # max_retries=2   → retry temporary API failures twice
    max_retries=2

    )

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


# # here we are calling the tools for the AI tasks, and also validating the each tool arguments.
# # ORD-1001   ✅
# # ORD-22     ❌

# # CUST-001   ✅
# # UST-001    ❌
# def execute_tool(name: str, arguments: dict) -> dict:
#     try:
#         if name == "get_order_status":
#             args = OrderStatusArgs.model_validate(arguments)

#             return get_order_status(
#                 order_id=args.order_id
#             )

#         if name == "create_support_ticket":
#             args = CreateTicketArgs.model_validate(arguments)

#             return create_support_ticket(
#                 customer_id=args.customer_id,
#                 issue=args.issue,
#                 order_id=args.order_id,
#             )

#         if name == "escalate_to_human":
#             args = EscalateArgs.model_validate(arguments)

#             return escalate_to_human(
#                 customer_id=args.customer_id,
#                 reason=args.reason,
#             )

#         if name == "request_refund":
#             args = RefundRequestArgs.model_validate(arguments)

#             return request_refund(
#                 customer_id=args.customer_id,
#                 order_id=args.order_id,
#                 reason=args.reason,
#             )

#         if name == "search_knowledge_base":

#             args = KnowledgeSearchArgs(**arguments)

#             return search_knowledge_base(
#                 question=args.question,
#             )

#         return {
#             "error": f"Unknown tool: {name}"
#         }

#     except ValidationError as error:
#         return {
#             "error": "Invalid tool arguments",
#             "details": error.errors(include_url=False),
#         }
#     except Exception:
#         return {
#             "error": "Tool execution failed"
#         }


#first we are giving query to AI
#then ai decides that do we need to use the tool or not 
#if yes, then we call the python tool and return the order id, and then we give this results again to AI.
#then AI gives us the final answer.
def generate_ai_reply(
    message: str,
    conversation_id: str,
) -> str:
    
    # adding the previous  context of the chat.
    input_list = get_conversation_messages(
    conversation_id=conversation_id
)
    instructions = """
        You are a customer-support assistant for this company.

        Use get_order_status for order-status questions.

        Use create_support_ticket when the customer wants a support ticket.

        Use escalate_to_human when the customer explicitly asks for a human
        or when the issue cannot be handled with the available tools.

        Use request_refund when the customer asks for a refund.
        Refund requests are only pending approval.
        Never tell the customer that a refund has been completed or approved.

        Never invent customer IDs or order IDs.
        Ask for required information when it is missing.

        Use search_knowledge_base for questions about company documentation,
        policies, instructions, products, delivery, returns, refunds,
        damaged items, cancellations, or other company information.

        For company-information questions, you MUST use search_knowledge_base
        before answering.

        Do not answer company-information questions from your own general knowledge.

        If search_knowledge_base returns found=false, clearly tell the user
        that the information is not available in the company knowledge base.

        For questions that are unrelated to customer support or the company,
        do not answer using general knowledge.
        Politely explain that you can only assist with company customer-support matters.

        Use relevant information already available in the conversation history.

        Do not invent company policies, documentation, or actions.
        Do not claim to perform actions that are not available through your tools.
        When search_knowledge_base returns relevant documentation,
        base your answer only on that documentation.

        When using information from search_knowledge_base,
        include the relevant source URL or URLs in the final response.

        Do not invent source URLs.
        Only use URLs returned by search_knowledge_base.

        When calling search_knowledge_base, make the search question
        self-contained using relevant conversation history.

        Resolve references such as "it", "that item", "that order",
        "they", or "this product" when the previous conversation
        makes their meaning clear.

        When search_knowledge_base returns relevant documentation,
        answer using that documentation and include the returned source URLs.

        Do not invent source URLs.
        """

    max_steps = 5
    max_tool_calls=8;
    tool_call_count=0;
    #limit total tool calls
    
    for _ in range(max_steps):

        response = client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            tools=tools,
            input=input_list,
        )

        input_list += response.output
        # Find all the tools that the AI requested.
        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # No tool requested → final answer
        if not function_calls:
            return response.output_text

        # Execute every requested tool
        for item in function_calls:
            arguments = json.loads(item.arguments)
            tool_call_count += 1

            if tool_call_count > max_tool_calls:
                return (
                    "Sorry, I could not safely complete the request "
                    "because too many actions were required."
                )

            result = execute_tool(
                name=item.name,
                arguments=arguments,
            )
            save_tool_call(
                conversation_id=conversation_id,
                tool_name=item.name,
                arguments=json.dumps(arguments),
                result=json.dumps(result),
            )
            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            )

    return "Sorry, I could not complete the request within the allowed steps."

# Now we need OpenAI to turn that raw tool result into a nice human answer.
# So the second request receives the complete history:(user input, first ai response, then tool output)
    final_response = client.responses.create(
        model=settings.openai_model,
        instructions="Give the customer a short and helpful answer.",
        tools=tools,
        input=input_list,
    )

    return final_response.output_text

#this is the final answer to the /chat. 