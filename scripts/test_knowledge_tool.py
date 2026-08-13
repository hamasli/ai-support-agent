from src.app.tools.knowledge_tools import search_knowledge_base


question = (
    "What is the company's policy if a delivered item arrives damaged? "
    "Include steps for reporting damage, required evidence, "
    "return/refund/replacement options, and any timelines."
)


result = search_knowledge_base(question)

print("\nFOUND:")
print(result["found"])

print("\nMODE:")
print(result["retrieval_mode"])

print("\nRESULTS:")

for index, item in enumerate(
    result["results"],
    start=1,
):
    print(f"\nResult {index}")
    print("Title:", item["title"])
    print("Source:", item["source_url"])
    print(
        "Content:",
        item["content"][:300],
        "...",
    )