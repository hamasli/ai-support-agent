from src.app.retrieval.query_rewriter import rewrite_query
from src.app.retrieval.reranker_service import rerank_results
from src.app.retrieval.retrieval_service import (
    search_knowledge_hybrid,
)


def search_knowledge_base(
    question: str,
) -> dict:

    # Step 1: rewrite user question for retrieval
    search_query = rewrite_query(question)

    # Step 2: vector + keyword hybrid retrieval
    candidates = search_knowledge_hybrid(
        question=search_query,
        limit=10,
        candidate_limit=10,
    )

    if not candidates:
        return {
            "found": False,
            "search_query": search_query,
            "message": "No relevant documentation found.",
        }

    # Step 3: rerank retrieved candidates
    results = rerank_results(
        question=question,
        candidates=candidates,
        limit=5,
    )
    MIN_RERANK_SCORE = 60

    results = [
        result
        for result in results
        if result["rerank_score"] >= MIN_RERANK_SCORE
    ]
    if not results:
        return {
            "found": False,
            "search_query": search_query,
            "message": "No relevant documentation found.",
        }

    return {
        "found": True,
        "search_query": search_query,
        "results": [
            {
                "id": result["id"],
                "title": result["title"],
                "content": result["content"],
                "source_url": result["source_url"],
                "similarity": result["similarity"],
                "keyword_score": result["keyword_score"],
                "hybrid_score": result["hybrid_score"],
                "rerank_score": result["rerank_score"],
            }
            for result in results
        ],
    }