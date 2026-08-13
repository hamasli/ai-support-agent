from src.app.retrieval.query_rewriter import rewrite_query
from src.app.retrieval.reranker_service import rerank_results
from src.app.retrieval.retrieval_service import (
    search_knowledge_hybrid,
)


# EVERY RAG QUESTION
# ↓
# rewrite with LLM 🐌
# ↓
# embedding
# ↓
# hybrid
# ↓
# rerank with LLM 🐌
#  This version has a greater latency, so we are not using this direclty.
# def search_knowledge_base(
#     question: str,
# ) -> dict:

#     # Step 1: rewrite user question for retrieval
#     search_query = rewrite_query(question)

#     # Step 2: vector + keyword hybrid retrieval
#     candidates = search_knowledge_hybrid(
#         question=search_query,
#         limit=10,
#         candidate_limit=10,
#     )

#     if not candidates:
#         return {
#             "found": False,
#             "search_query": search_query,
#             "message": "No relevant documentation found.",
#         }

#     # Step 3: rerank retrieved candidates
#     results = rerank_results(
#         question=question,
#         candidates=candidates,
#         limit=5,
#     )
#     MIN_RERANK_SCORE = 60

#     results = [
#         result
#         for result in results
#         if result["rerank_score"] >= MIN_RERANK_SCORE
#     ]
#     if not results:
#         return {
#             "found": False,
#             "search_query": search_query,
#             "message": "No relevant documentation found.",
#         }

#     return {
#         "found": True,
#         "search_query": search_query,
#         "results": [
#             {
#                 "id": result["id"],
#                 "title": result["title"],
#                 "content": result["content"],
#                 "source_url": result["source_url"],
#                 "similarity": result["similarity"],
#                 "keyword_score": result["keyword_score"],
#                 "hybrid_score": result["hybrid_score"],
#                 "rerank_score": result["rerank_score"],
#             }
#             for result in results
#         ],
#     }






# Question
# ↓
# Hybrid search
# ↓
# Strong result?
# ├── YES → return immediately ⚡
# │
# └── NO
#      ↓
#    rewrite
#      ↓
#    hybrid
#      ↓
#    rerank
#      ↓
#    threshold
# from src.app.retrieval.query_rewriter import rewrite_query
# from src.app.retrieval.reranker_service import rerank_results
# from src.app.retrieval.retrieval_service import (
#     search_knowledge_hybrid,
# )


FAST_MIN_SIMILARITY = 0.50
FAST_MIN_KEYWORD_SCORE = 0.01

ADVANCED_MIN_RERANK_SCORE = 60


# def search_knowledge_base(
#     question: str,
# ) -> dict:

   
#     # STEP 1: FAST PATH
#     # Hybrid retrieval using original question
   

#     fast_results = search_knowledge_hybrid(
#         question=question,
#         limit=5,
#         candidate_limit=10,
#     )

#     if fast_results:

#         best_result = fast_results[0]

#         strong_vector_match = (
#             best_result["similarity"]
#             >= FAST_MIN_SIMILARITY
#         )

#         strong_keyword_match = (
#             best_result["keyword_score"]
#             >= FAST_MIN_KEYWORD_SCORE
#         )

#         # Good evidence -> return immediately
#         if (
#             strong_vector_match
#             or strong_keyword_match
#         ):
#             return {
#                 "found": True,
#                 "retrieval_mode": "hybrid_fast",
#                 "search_query": question,
#                 "results": fast_results,
#             }

   
#     # STEP 2: ADVANCED FALLBACK
#     # Rewrite vague/weak query
    

#     rewritten_query = rewrite_query(
#         question
#     )

#     candidates = search_knowledge_hybrid(
#         question=rewritten_query,
#         limit=10,
#         candidate_limit=10,
#     )

#     if not candidates:
#         return {
#             "found": False,
#             "retrieval_mode": "advanced_fallback",
#             "search_query": rewritten_query,
#             "message": (
#                 "No relevant documentation found."
#             ),
#         }

   
#     # STEP 3: RERANK ONLY WHEN NECESSARY
    

#     reranked_results = rerank_results(
#         question=question,
#         candidates=candidates,
#         limit=5,
#     )

#     relevant_results = [
#         result
#         for result in reranked_results
#         if result["rerank_score"]
#         >= ADVANCED_MIN_RERANK_SCORE
#     ]

#     if not relevant_results:
#         return {
#             "found": False,
#             "retrieval_mode": "advanced_fallback",
#             "search_query": rewritten_query,
#             "message": (
#                 "No relevant documentation found."
#             ),
#         }

#     return {
#         "found": True,
#         "retrieval_mode": "advanced_fallback",
#         "search_query": rewritten_query,
#         "results": relevant_results,
#     }

import time;
def search_knowledge_base(
    question: str,
) -> dict:

    rag_start = time.perf_counter()

    # --------------------------------------------------
    # FAST HYBRID SEARCH
    # --------------------------------------------------

    hybrid_start = time.perf_counter()

    fast_results = search_knowledge_hybrid(
        question=question,
        limit=5,
        candidate_limit=10,
    )

    hybrid_time = time.perf_counter() - hybrid_start

    print(
        f"[RAG] Fast hybrid search: "
        f"{hybrid_time:.2f}s"
    )

    if fast_results:

        best_result = fast_results[0]

        strong_vector_match = (
            best_result["similarity"]
            >= FAST_MIN_SIMILARITY
        )

        strong_keyword_match = (
            best_result["keyword_score"]
            >= FAST_MIN_KEYWORD_SCORE
        )

        if (
            strong_vector_match
            or strong_keyword_match
        ):

            total_time = (
                time.perf_counter()
                - rag_start
            )

            print(
                "[RAG] MODE: hybrid_fast"
            )

            print(
                f"[RAG] TOTAL: "
                f"{total_time:.2f}s"
            )

            return {
                "found": True,
                "retrieval_mode": "hybrid_fast",
                "results": compact_results(
                    fast_results,
                    limit=3,
                ),
}

    # --------------------------------------------------
    # FALLBACK: QUERY REWRITE
    # --------------------------------------------------

    rewrite_start = time.perf_counter()

    rewritten_query = rewrite_query(
        question
    )

    rewrite_time = (
        time.perf_counter()
        - rewrite_start
    )

    print(
        f"[RAG] Query rewriting: "
        f"{rewrite_time:.2f}s"
    )

    # --------------------------------------------------
    # SECOND HYBRID SEARCH
    # --------------------------------------------------

    second_search_start = time.perf_counter()

    candidates = search_knowledge_hybrid(
        question=rewritten_query,
        limit=10,
        candidate_limit=10,
    )

    second_search_time = (
        time.perf_counter()
        - second_search_start
    )

    print(
        f"[RAG] Second hybrid search: "
        f"{second_search_time:.2f}s"
    )

    if not candidates:
        return {
            "found": False,
            "retrieval_mode": "advanced_fallback",
            "search_query": rewritten_query,
            "message": (
                "No relevant documentation found."
            ),
        }

    # --------------------------------------------------
    # RERANKING
    # --------------------------------------------------

    rerank_start = time.perf_counter()

    reranked_results = rerank_results(
        question=question,
        candidates=candidates,
        limit=5,
    )

    rerank_time = (
        time.perf_counter()
        - rerank_start
    )

    print(
        f"[RAG] Reranking: "
        f"{rerank_time:.2f}s"
    )

    relevant_results = [
        result
        for result in reranked_results
        if result["rerank_score"]
        >= ADVANCED_MIN_RERANK_SCORE
    ]

    total_time = (
        time.perf_counter()
        - rag_start
    )

    print(
        "[RAG] MODE: advanced_fallback"
    )

    print(
        f"[RAG] TOTAL: "
        f"{total_time:.2f}s"
    )

    if not relevant_results:
        return {
            "found": False,
            "retrieval_mode": "advanced_fallback",
            "search_query": rewritten_query,
            "message": (
                "No relevant documentation found."
            ),
        }

    return {
        "found": True,
        "retrieval_mode": "advanced_fallback",
        "results": compact_results(
            relevant_results,
            limit=3,
        ),
}


def compact_results(
    results: list[dict],
    limit: int = 3,
) -> list[dict]:

    return [
        {
            "title": result["title"],
            "source_url": result["source_url"],
            "content": result["content"],
        }
        for result in results[:limit]
    ]