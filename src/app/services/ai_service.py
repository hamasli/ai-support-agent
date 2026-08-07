
import json

from openai import OpenAI

from src.app.core.config import settings
from src.app.tools.order_tools import get_order_status
from src.app.tools.support_tools import create_support_ticket;

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
}

]

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
            "Use create_support_ticket when the customer asks to create a support ticket. "
            "Never invent an order ID or customer ID. "
            "If required information is missing, ask the user for it. "
            "Do not offer actions that are not available through your tools."
                ),
        tools=tools,
        input=input_list,
    )
    #combining what user wants, and the model request. and later we will use this also. at the end.
    input_list += response.output

    tool_was_called = False

    for item in response.output:
        if item.type == "function_call" and item.name == "get_order_status":
            arguments = json.loads(item.arguments)

            #python is running the tool.
            result = get_order_status(
                order_id=arguments["order_id"]
            )

            #now here we have tell openai what happend.
            # AI tool request #123
            #    ↓
            # Python executes it
            #     ↓
            # Tool result for request #123
            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    #call id connects the results to the exact tool call the model mode.
                    "output": json.dumps(result),
                }
            )

            tool_was_called = True
        elif item.type=="function_call" and item.name=="create_support_ticket":
            arguments=json. loads(item.arguments)
            result=create_support_ticket(
                customer_id=arguments["customer_id"],
                issue=arguments["issue"],
            )

            input_list.append(
                {
                    "type":"function_call_output",
                    "call_id":item.call_id,
                    "output":json.dumps(result),
                }
            )
            tool_was_called=True


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