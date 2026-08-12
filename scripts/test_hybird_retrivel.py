from src.app.retrieval.retrieval_service import (
    search_knowledge_hybrid,
)


QUESTION = "How long can I return an item with a receipt?"


results = search_knowledge_hybrid(
    question=QUESTION,
    limit=5,
)


for index, result in enumerate(
    results,
    start=1,
):
    print(f"\nRESULT {index}")

    print(
        "Hybrid:",
        result["hybrid_score"],
    )

    print(
        "Vector similarity:",
        result["similarity"],
    )

    print(
        "Keyword score:",
        result["keyword_score"],
    )

    print("Title:", result["title"])
    print("Source:", result["source_url"])

    print("Content:")
    print(result["content"][:400])