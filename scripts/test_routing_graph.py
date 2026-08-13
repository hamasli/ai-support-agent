from src.app.agents.routing_graph import routing_graph


test_1 = {
    "conversation_id": "CONV-TEST-1",
    "messages": [
        {
            "role": "user",
            "content": "Where is my order?",
        }
    ],
}


test_2 = {
    "conversation_id": "CONV-TEST-2",
    "messages": [
        {
            "role": "user",
            "content": "Hello there",
        }
    ],
}


print("\nTEST 1")

result_1 = routing_graph.invoke(test_1)

print(result_1)


print("\nTEST 2")

result_2 = routing_graph.invoke(test_2)

print(result_2)