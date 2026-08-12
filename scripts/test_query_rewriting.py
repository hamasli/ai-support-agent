from src.app.retrieval.query_rewriter import (
    rewrite_query,
)


questions = [
    "What if my thing comes broken?",
    "Can I send it back?",
    "How long do I have if I still have the receipt?",
]


for question in questions:

    rewritten = rewrite_query(question)

    print("\nORIGINAL:")
    print(question)

    print("REWRITTEN:")
    print(rewritten)