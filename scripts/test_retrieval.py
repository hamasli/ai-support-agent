from src.app.retrieval.retrieval_service import search_knowledge


QUESTION = "How do I make a POST request using HTTPX?"


results = search_knowledge(
    question=QUESTION,
    limit=3,
)


for index, result in enumerate(results, start=1):

    print(f"\nRESULT {index}")
    print("Similarity:", result["similarity"])
    print("Title:", result["title"])
    print("Source:", result["source_url"])
    print("Content:")
    print(result["content"][:500])