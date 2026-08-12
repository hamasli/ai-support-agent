from pydantic import BaseModel, Field
from openai import OpenAI

from src.app.core.config import settings


client = OpenAI(
    api_key=settings.openai_api_key,
)


class RankedChunk(BaseModel):
    id: int
    score: int = Field(
        ge=0,
        le=100,
    )


class RerankResponse(BaseModel):
    results: list[RankedChunk]


def rerank_results(
    question: str,
    candidates: list[dict],
    limit: int = 5,
) -> list[dict]:

    if not candidates:
        return []

    candidate_text = "\n\n".join(
        (
            f"CHUNK ID: {candidate['id']}\n"
            f"TITLE: {candidate['title']}\n"
            f"CONTENT:\n{candidate['content']}"
        )
        for candidate in candidates
    )

    response = client.responses.parse(
        model=settings.openai_model,
        instructions="""
You are a retrieval reranker.

Rank the provided document chunks by how useful they are
for answering the user's question.

Score each chunk from 0 to 100.

100 = directly answers the question.
0 = completely irrelevant.

Only use chunk IDs that were provided.
Do not answer the user's question.
""",
        input=f"""
USER QUESTION:

{question}


CANDIDATE CHUNKS:

{candidate_text}
""",
        text_format=RerankResponse,
    )

    parsed = response.output_parsed

    if parsed is None:
        return candidates[:limit]

    candidates_by_id = {
        candidate["id"]: candidate
        for candidate in candidates
    }

    ranked_items = sorted(
        parsed.results,
        key=lambda item: item.score,
        reverse=True,
    )

    reranked_results = []

    for item in ranked_items:

        candidate = candidates_by_id.get(
            item.id
        )

        if candidate is None:
            continue

        result = candidate.copy()

        result["rerank_score"] = item.score

        reranked_results.append(result)

    return reranked_results[:limit]