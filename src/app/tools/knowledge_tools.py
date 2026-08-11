from src.app.retrieval.retrieval_service import search_knowledge


def search_knowledge_base(question: str) -> dict:

    results = search_knowledge(
        question=question,
        limit=5,
    )

    if not results:
        return {
            "found": False,
            "message": "No relevant documentation found.",
        }

    return {
        "found": True,
        "results": [
            {
                "content": result["content"],
                "source_url": result["source_url"],
                "title": result["title"],
                "similarity": result["similarity"],
            }
            for result in results
        ],
    }