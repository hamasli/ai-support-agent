from fastapi.testclient import TestClient

from src.app.main import app
from src.app.api.routes import chat
from src.app.api.routes import refunds


client = TestClient(app)



# CHAT API - INVALID CONVERSATION


def test_chat_invalid_conversation_returns_404(
    monkeypatch,
):
    """
    Do not use the real database here.

    Pretend conversation_exists() returned False
    and verify that /chat handles it correctly.
    """

    monkeypatch.setattr(
        chat,
        "conversation_exists",
        lambda conversation_id: False,
    )

    response = client.post(
        "/chat",
        json={
            "message": "Hello",
            "conversation_id": "CONV-FAKE123",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Conversation not found."
    )



# REFUND REVIEW API - SUCCESS


def test_refund_review_endpoint_success(
    monkeypatch,
):
    """
    Test the FastAPI refund-review endpoint
    without running the real LangGraph workflow.

    We already tested the real HITL workflow manually.
    Here we only verify that the API route correctly
    handles a successful review result.
    """

    # Pretend the conversation exists.
    monkeypatch.setattr(
        refunds,
        "conversation_exists",
        lambda conversation_id: True,
    )

    # Pretend LangGraph resumed successfully.
    monkeypatch.setattr(
        refunds,
        "resume_refund_review",
        lambda conversation_id,
        refund_id,
        approved: {
            "final_response": (
                "Your refund request has "
                "been approved."
            )
        },
    )

    # Do not write a real assistant message
    # into PostgreSQL during this API test.
    monkeypatch.setattr(
        refunds,
        "save_message",
        lambda **kwargs: None,
    )

    response = client.post(
        "/refunds/REF-TEST123/review",
        json={
            "conversation_id": "CONV-TEST123",
            "approved": True,
        },
    )

    assert response.status_code == 200

    body = response.json()

    # Old fields
    assert body["conversation_id"] == "CONV-TEST123"
    assert body["refund_id"] == "REF-TEST123"

    assert body["reply"] == (
        "Your refund request has been approved."
    )

    # New structured response fields
    assert body["status"] == "completed"

    assert body["requires_human_review"] is False

    assert (
        body["data"]["refund_id"]
        == "REF-TEST123"
    )

    assert (
        body["data"]["refund_status"]
        == "approved"
    )