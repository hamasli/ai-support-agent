from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

examples = client.list_examples(
    dataset_name="ai-support-agent-evaluation"
)

for number, example in enumerate(examples, start=1):
    print(f"\nEXAMPLE {number}")
    print(example.inputs)