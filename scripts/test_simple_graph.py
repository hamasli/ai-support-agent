from src.app.agents.simple_graph import simple_graph


initial_state = {
    "conversation_id": "CONV-TEST",
    "messages": [
        {
            "role": "user",
            "content": "Hello LangGraph",
        }
    ],
}


result = simple_graph.invoke(
    initial_state
)


print("\nFINAL STATE:")
print(result)