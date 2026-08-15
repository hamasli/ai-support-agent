from src.app.services.tool_service import execute_tool
from src.app.tools import knowledge_tools


# KNOWLEDGE TOOL - STRONG RESULT


def test_search_knowledge_base_found(
    monkeypatch,
):
    """
    Fake hybrid retrieval so pytest does not
    call the real embedding/OpenAI service.
    """

    fake_results = [
        {
            "id": 1,
            "title": "Damaged Item Policy",
            "source_url": (
                "https://example.com/damaged-items"
            ),
            "content": (
                "Customers should report damaged "
                "items through support."
            ),
            "similarity": 0.85,
            "keyword_score": 0.20,
            "hybrid_score": 0.90,
        }
    ]

    # Replace the real retrieval function only
    # during this test.
    monkeypatch.setattr(
        knowledge_tools,
        "search_knowledge_hybrid",
        lambda **kwargs: fake_results,
    )

    result = (
        knowledge_tools.search_knowledge_base(
            "What should I do if my item is damaged?"
        )
    )

    assert result["found"] is True

    assert (
        result["retrieval_mode"]
        == "hybrid_fast"
    )

    assert len(result["results"]) == 1

    assert (
        result["results"][0]["title"]
        == "Damaged Item Policy"
    )

    assert (
        result["results"][0]["source_url"]
        == "https://example.com/damaged-items"
    )



# KNOWLEDGE TOOL - NO RELEVANT RESULT


def test_search_knowledge_base_not_found(
    monkeypatch,
):
    """
    Simulate:
    - first hybrid search finds nothing
    - rewritten search also finds nothing
    """

    # Both hybrid searches return no candidates.
    monkeypatch.setattr(
        knowledge_tools,
        "search_knowledge_hybrid",
        lambda **kwargs: [],
    )

    # Avoid calling the real LLM query rewriter.
    monkeypatch.setattr(
        knowledge_tools,
        "rewrite_query",
        lambda question: question,
    )

    result = (
        knowledge_tools.search_knowledge_base(
            "Completely unrelated question"
        )
    )

    assert result["found"] is False

    assert (
        result["retrieval_mode"]
        == "advanced_fallback"
    )

    assert (
        result["message"]
        == "No relevant documentation found."
    )


# TOOL SERVICE - UNKNOWN TOOL


def test_execute_unknown_tool():

    result = execute_tool(
        name="tool_that_does_not_exist",
        arguments={},
    )

    assert "error" in result

    assert result["error"] == (
        "Unknown tool: "
        "tool_that_does_not_exist"
    )



# TOOL SERVICE - INVALID ARGUMENTS


def test_execute_tool_invalid_arguments():
    """
    get_order_status requires a valid order_id.

    Sending an empty argument dictionary should
    fail Pydantic validation instead of crashing.
    """

    result = execute_tool(
        name="get_order_status",
        arguments={},
    )

    assert "error" in result

    assert (
        result["error"]
        == "Invalid tool arguments"
    )

    assert "details" in result