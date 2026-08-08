
import json

from openai import OpenAI
from pydantic import ValidationError

from src.app.core.config import settings
from src.app.tools.order_tools import get_order_status
from src.app.tools.support_tools import (
    create_support_ticket,
    escalate_to_human,
    request_refund,
)
from src.app.schemas.tool_schemas import (
    OrderStatusArgs,
    CreateTicketArgs,
    EscalateArgs,
    RefundRequestArgs,
)

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
}

]


# here we are calling the tools for the AI tasks, and also validating the each tool arguments.
# ORD-1001   ✅
# ORD-22     ❌

# CUST-001   ✅
# UST-001    ❌
def execute_tool(name: str, arguments: dict) -> dict:
    try:
        if name == "get_order_status":
            args = OrderStatusArgs.model_validate(arguments)

            return get_order_status(
                order_id=args.order_id
            )

        if name == "create_support_ticket":
            args = CreateTicketArgs.model_validate(arguments)

            return create_support_ticket(
                customer_id=args.customer_id,
                issue=args.issue,
                order_id=args.order_id,
            )

        if name == "escalate_to_human":
            args = EscalateArgs.model_validate(arguments)

            return escalate_to_human(
                customer_id=args.customer_id,
                reason=args.reason,
            )

        if name == "request_refund":
            args = RefundRequestArgs.model_validate(arguments)

            return request_refund(
                customer_id=args.customer_id,
                order_id=args.order_id,
                reason=args.reason,
            )

        return {
            "error": f"Unknown tool: {name}"
        }

    except ValidationError as error:
        return {
            "error": "Invalid tool arguments",
            "details": error.errors(include_url=False),
        }
    except Exception:
        return {
            "error": "Tool execution failed"
        }


#first we are giving query to AI
#then ai decides that do we need to use the tool or not 
#if yes, then we call the python tool and return the order id, and then we give this results again to AI.
#then AI gives us the final answer.
def generate_ai_reply(message: str) -> str:
    input_list = [
        {
            "role": "user",
            "content": message,
        }
    ]

    instructions = (
        "You are a customer-support assistant. "
        "Use get_order_status for order-status questions. "
        "Use create_support_ticket when the customer wants a support ticket. "
        "Use escalate_to_human when the customer explicitly asks for a human "
        "or when the issue cannot be handled with the available tools. "
        "Never invent customer IDs or order IDs. "
        "Use request_refund when the customer asks for a refund. "
        "Refund requests are only pending approval;"
        " never tell the customer that a refund has been completed or approved. "
        "Ask for required information when it is missing. "
        "Do not claim to perform actions that are not available through your tools."
    )

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