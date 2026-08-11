from openai import OpenAI

from src.app.core.config import settings
from src.app.retrieval.retrieval_service import search_knowledge


client = OpenAI(
    api_key=settings.openai_api_key,
)


def answer_with_rag(question: str) -> dict:

    results = search_knowledge(
        question=question,
        limit=5,
    )

     # joining the context of all the  chunks results.
    context = "\n\n---\n\n".join(
        result["content"]
        for result in results
    )

    response = client.responses.create(
        model=settings.openai_model,
        instructions=(
            "You are a support assistant. "
            "Answer the question using only the provided context. "
            "If the context does not contain the answer, say that "
            "you do not have enough information. "
            "Do not invent information."
        ),
        input=f"""
CONTEXT:

{context}

QUESTION:

{question}
""",
    )
    #this collects the URLS from the retrived chunks.
    sources = list(
        dict.fromkeys(
            result["source_url"]
            for result in results
        )
    )

    return {
        "answer": response.output_text,
        "sources": sources,
    }