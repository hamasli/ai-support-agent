from dotenv import load_dotenv
from langsmith import Client


load_dotenv()

DATASET_NAME = "ai-support-agent-evaluation"

client = Client()


# ---------------------------------------------------------
# DELETE CURRENT BAD EXAMPLES
# ---------------------------------------------------------

examples = list(
    client.list_examples(
        dataset_name=DATASET_NAME
    )
)

for example in examples:
    client.delete_example(
        example_id=example.id
    )

print(
    f"Deleted {len(examples)} old examples."
)


# ---------------------------------------------------------
# CREATE CORRECT EXAMPLES
# ---------------------------------------------------------

correct_examples = [
    {
        "inputs": {
            "message":
                "What is your company's return policy?"
        }
    },
    {
        "inputs": {
            "message":
                "What should I do if my item arrives damaged?"
        }
    },
    {
        "inputs": {
            "message":
                "What is the status of order ORD-9005 "
                "for customer CUST-902?"
        }
    },
    {
        "inputs": {
            "message":
                "What is the status of order "
                "ORD-DOES-NOT-EXIST?"
        }
    },
    {
        "inputs": {
            "message":
                "I want a refund for ORD-9005."
        }
    },
]


client.create_examples(
    dataset_name=DATASET_NAME,
    examples=correct_examples,
)

print("Created 5 correct examples.")