import time

from src.app.retrieval.query_rewriter import rewrite_query
from src.app.retrieval.reranker_service import rerank_results
from src.app.retrieval.retrieval_service import (
    search_knowledge,
    search_knowledge_hybrid,
)


RETURN_POLICY = (
    "https://www.ikea.com/gb/en/customer-service/"
    "returns-claims/return-policy/"
)

DAMAGED_ITEM = (
    "https://www.ikea.com/gb/en/customer-service/knowledge/"
    "articles/06gd5116-29d3-41c9-ge22-c23425737816.html"
)

MANAGE_ORDER = (
    "https://www.ikea.com/gb/en/customer-service/"
    "track-manage-order/"
)

DELIVERY = (
    "https://www.ikea.com/gb/en/customer-service/"
    "services/delivery/"
)


TEST_CASES = [
    {
        "question": "How long do I have to return an item with a receipt?",
        "expected_sources": [
            RETURN_POLICY,
            MANAGE_ORDER,
        ],
    },
    {
        "question": "Can I return an opened item?",
        "expected_sources": [
            RETURN_POLICY,
        ],
    },
    {
        "question": "What if my item arrives damaged?",
        "expected_sources": [
            DAMAGED_ITEM,
        ],
    },
    {
        "question": "Can I get a replacement for a damaged delivery?",
        "expected_sources": [
            DAMAGED_ITEM,
        ],
    },
    {
        "question": "Can I get a refund if my delivered product is damaged?",
        "expected_sources": [
            DAMAGED_ITEM,
            RETURN_POLICY,
        ],
    },
    {
        "question": "Can I cancel my order?",
        "expected_sources": [
            MANAGE_ORDER,
        ],
    },
    {
        "question": "How can I track my order?",
        "expected_sources": [
            MANAGE_ORDER,
        ],
    },
    {
        "question": "What delivery options are available?",
        "expected_sources": [
            DELIVERY,
        ],
    },
]


def is_correct(
    results: list[dict],
    expected_sources: list[str],
) -> bool:

    returned_sources = {
        result["source_url"]
        for result in results
    }

    return any(
        source in returned_sources
        for source in expected_sources
    )


vector_correct = 0
hybrid_correct = 0
advanced_correct = 0

vector_time = 0.0
hybrid_time = 0.0
advanced_time = 0.0


for number, test in enumerate(
    TEST_CASES,
    start=1,
):
    question = test["question"]
    expected_sources = test["expected_sources"]

    print("\n" + "=" * 70)
    print(f"TEST {number}")
    print("Question:", question)

    # -------------------------------------------------
    # 1. VECTOR ONLY
    # -------------------------------------------------

    start = time.perf_counter()

    vector_results = search_knowledge(
        question=question,
        limit=5,
        min_similarity=None,
    )

    vector_elapsed = time.perf_counter() - start
    vector_time += vector_elapsed

    vector_hit = is_correct(
        vector_results,
        expected_sources,
    )

    if vector_hit:
        vector_correct += 1

    # -------------------------------------------------
    # 2. HYBRID
    # -------------------------------------------------

    start = time.perf_counter()

    hybrid_results = search_knowledge_hybrid(
        question=question,
        limit=5,
        candidate_limit=10,
    )

    hybrid_elapsed = time.perf_counter() - start
    hybrid_time += hybrid_elapsed

    hybrid_hit = is_correct(
        hybrid_results,
        expected_sources,
    )

    if hybrid_hit:
        hybrid_correct += 1

    # -------------------------------------------------
    # 3. FULL ADVANCED RETRIEVAL
    # query rewrite + hybrid + reranking
    # -------------------------------------------------

    start = time.perf_counter()

    rewritten_query = rewrite_query(question)

    candidates = search_knowledge_hybrid(
        question=rewritten_query,
        limit=10,
        candidate_limit=10,
    )

    advanced_results = rerank_results(
        question=question,
        candidates=candidates,
        limit=5,
    )

    advanced_elapsed = time.perf_counter() - start
    advanced_time += advanced_elapsed

    advanced_hit = is_correct(
        advanced_results,
        expected_sources,
    )

    if advanced_hit:
        advanced_correct += 1

    # -------------------------------------------------
    # PRINT RESULT
    # -------------------------------------------------

    print("\nRewritten:")
    print(rewritten_query)

    print("\nVector only:", "PASS" if vector_hit else "FAIL")
    if vector_results:
        print(
            "Top result:",
            vector_results[0]["title"],
        )

    print("\nHybrid:", "PASS" if hybrid_hit else "FAIL")
    if hybrid_results:
        print(
            "Top result:",
            hybrid_results[0]["title"],
        )

    print(
        "\nRewrite + Hybrid + Reranker:",
        "PASS" if advanced_hit else "FAIL",
    )

    if advanced_results:
        print(
            "Top result:",
            advanced_results[0]["title"],
        )
        print(
            "Rerank score:",
            advanced_results[0]["rerank_score"],
        )


total = len(TEST_CASES)

print("\n\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)

print(
    f"Vector only: {vector_correct}/{total} "
    f"({vector_correct / total:.0%})"
)

print(
    f"Hybrid: {hybrid_correct}/{total} "
    f"({hybrid_correct / total:.0%})"
)

print(
    f"Advanced: {advanced_correct}/{total} "
    f"({advanced_correct / total:.0%})"
)

print("\nAVERAGE LATENCY")

print(
    f"Vector: {vector_time / total:.2f}s"
)

print(
    f"Hybrid: {hybrid_time / total:.2f}s"
)

print(
    f"Advanced: {advanced_time / total:.2f}s"
)