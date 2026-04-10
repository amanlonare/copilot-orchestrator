from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.presentation.api.app import app

client = TestClient(app)


def test_health_check() -> None:
    """Test the health endpoint returns OK."""
    ok_status = 200
    response = client.get("/health")
    assert response.status_code == ok_status
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_endpoint_delegation() -> None:
    """Test that the chat endpoint correctly validates schemas and delegates to the graph."""
    # Mock result state
    mock_final_state = {
        "session": Session(session_id="test-session"),
        "answer": AgentMessage(role=MessageRole.ASSISTANT, content="Hello from mock"),
        "retrieved_result": None,
        "fallback_flag": False,
        "trace_metadata": {"node": "finalize"},
    }

    # We need to mock the ainvoke method of the graph
    patch_path = "copilot_orchestrator.presentation.api.dependencies.orchestrator_graph.ainvoke"
    with patch(patch_path, new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_final_state

        ok_status = 200
        response = client.post("/chat", json={"query": "Hello", "session_id": "test-session"})

        assert response.status_code == ok_status
        data = response.json()
        assert data["answer"] == "Hello from mock"
        assert data["session_id"] == "test-session"
        mock_invoke.assert_called_once()


def test_chat_validation_error() -> None:
    """Test that invalid request schemas result in 422 Unprocessable Entity."""
    val_error_status = 422
    response = client.post(
        "/chat",
        json={"wrong_key": "data"},  # Missing 'query'
    )
    assert response.status_code == val_error_status
