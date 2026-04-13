from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.presentation.api.app import app
from copilot_orchestrator.presentation.api.dependencies import get_orchestrator_graph, get_services

client = TestClient(app)


def test_health_check() -> None:
    """Test the health endpoint returns OK."""
    ok_status = 200
    response = client.get("/v1/health")
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

    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = mock_final_state

    async def override_get_orchestrator_graph() -> AsyncGenerator[AsyncMock, None]:
        yield mock_graph

    def override_get_services() -> dict[str, Any]:
        return {"_telemetry": []}

    app.dependency_overrides[get_orchestrator_graph] = override_get_orchestrator_graph
    app.dependency_overrides[get_services] = override_get_services

    try:
        ok_status = 200
        response = client.post("/v1/chat", json={"query": "Hello", "session_id": "test-session"})

        assert response.status_code == ok_status
        data = response.json()
        assert data["answer"] == "Hello from mock"
        assert data["session_id"] == "test-session"
        mock_graph.ainvoke.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_chat_validation_error() -> None:
    """Test that invalid request schemas result in 422 Unprocessable Entity."""
    val_error_status = 422
    response = client.post(
        "/v1/chat",
        json={"wrong_key": "data"},  # Missing 'query'
    )
    assert response.status_code == val_error_status
