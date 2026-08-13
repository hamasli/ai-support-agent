from src.app.services.tool_service import execute_tool


result = execute_tool(
    name="search_knowledge_base",
    arguments={
        "question": (
            "What is the company's policy if a delivered "
            "item arrives damaged?"
        )
    },
)


print("\nRESULT:")
print(result)