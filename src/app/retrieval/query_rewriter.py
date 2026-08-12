from openai import OpenAI

from src.app.core.config import settings


client = OpenAI(
    api_key=settings.openai_api_key,
)


def rewrite_query(question: str) -> str:

    response = client.responses.create(
        model=settings.openai_model,
        instructions="""
You rewrite customer-support questions into concise search queries
for a company knowledge base.

Preserve important information such as:
- product names
- order IDs
- policy names
- delivery problems
- refund or return intent

Make the query clear and optimized for document retrieval.

Do not answer the question.
Do not invent information.

Return only the rewritten search query.
""",
        input=question,
    )

    rewritten = response.output_text.strip()

    if not rewritten:
        return question

    return rewritten