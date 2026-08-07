
import json

from openai import OpenAI
from pydantic import ValidationError

from src.app.core.config import settings
from src.app.tools.order_tools import get_order_status
from src.app.tools.support_tools import create_support_ticket;
from src.app.tools.support_tools import escalate_to_human;
from src.app.schemas.tool_schemas import OrderStatusArgs,CreateTicketArgs,EscalateArgs;



client = OpenAI(api_key=settings.openai_api_key)

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
    "description": "Create a support ticket for a customer.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID, for example CUST-001",
            },
            "issue": {
                "type": "string",
                "description": "Description of the customer's problem",
            },
        },
        "required": ["customer_id", "issue"],
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
            )

        if name == "escalate_to_human":
            args = EscalateArgs.model_validate(arguments)

            return escalate_to_human(
                customer_id=args.customer_id,
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

    response = client.responses.create(
        model=settings.openai_model,
        instructions=(
            "You are a customer-support assistant. "
            "Use get_order_status for order-status questions. "
            "Use create_support_ticket when the customer wants a support ticket. "
            "Use escalate_to_human when the customer explicitly asks for a human "
            "or when the issue cannot be handled with the available tools. "
            "Never invent customer IDs or order IDs. "
            "Ask for required information when it is missing. "
            "Do not claim to perform actions that are not available through your tools."
        ),
        tools=tools,
        input=input_list,
    )
    #combining what user wants, and the model request. and later we will use this also. at the end.
    input_list += response.output

    tool_was_called = False

    for item in response.output:

        print(item.type);
        if item.type != "function_call":
            continue

        arguments = json.loads(item.arguments)
        
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

        tool_was_called = True

    if not tool_was_called:
        return response.output_text

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