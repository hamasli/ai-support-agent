from src.app.retrieval.retrieval_service import (
    search_knowledge_keyword,
)


QUESTION = "365 days return receipt"


results = search_knowledge_keyword(
    question=QUESTION,
    limit=5,
)


for index, result in enumerate(
    results,
    start=1,
):
    print(f"\nRESULT {index}")
    print(
        "Keyword score:",
        result["keyword_score"],
    )
    print("Title:", result["title"])
    print("Source:", result["source_url"])
    print("Content:")
    print(result["content"][:500])