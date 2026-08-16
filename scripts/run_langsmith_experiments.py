import httpx

from dotenv import load_dotenv
from langsmith import Client


# Load LANGSMITH_API_KEY from .env
load_dotenv()


DATASET_NAME = "ai-support-agent-evaluation"

API_URL = "http://localhost:8001/chat"


def target(inputs: dict) -> dict:
    """
    Send one LangSmith dataset question
    to our real Dockerized FastAPI agent.
    """

    response = httpx.post(
        API_URL,
        json={
            "message": inputs["message"],
        },
        timeout=60.0,
    )

    response.raise_for_status()

    data = response.json()

    # These become the experiment outputs.
    return {
        "reply": data["reply"],
        "status": data["status"],
        "requires_human_review": data[
            "requires_human_review"
        ],
    }


client = Client()


results = client.evaluate(
    target,
    data=DATASET_NAME,

    # No evaluator yet.
    # First we only want real agent outputs.
    evaluators=[],

    experiment_prefix="baseline-agent",

    # Run one question at a time.
    max_concurrency=1,
)


print("\nExperiment completed.")
print(results)