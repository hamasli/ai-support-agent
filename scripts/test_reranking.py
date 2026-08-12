from src.app.retrieval.retrieval_service import (
    search_knowledge_hybrid,
)
from src.app.retrieval.reranker_service import (
    rerank_results,
)


QUESTION = (
    "What should I do if my item "
    "arrives damaged?"
)


candidates = search_knowledge_hybrid(
    question=QUESTION,
    limit=10,
    candidate_limit=10,
)


print("\n--- BEFORE RERANKING ---")

for index, result in enumerate(
    candidates,
    start=1,
):
    print(
        index,
        result["id"],
        result["title"],
        result["hybrid_score"],
    )


results = rerank_results(
    question=QUESTION,
    candidates=candidates,
    limit=5,
)


print("\n--- AFTER RERANKING ---")

for index, result in enumerate(
    results,
    start=1,
):
    print(
        index,
        result["id"],
        result["title"],
        "Rerank:",
        result["rerank_score"],
    )

    print(
        result["content"][:300]
    )

    print()