from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from copilot_orchestrator.presentation.api.app import app
from copilot_orchestrator.presentation.api.dependencies import get_orchestrator_graph, get_services


@pytest.fixture
def mock_graph() -> MagicMock:
    graph = MagicMock()

    # Mock data to stream - aligned with LangGraph astream_events v2 schema
    async def mock_events(*args: Any, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        events = [
            {"event": "on_chain_start", "name": "LangGraph", "data": {}},
            {"event": "on_node_start", "name": "detect_intent", "data": {}},
            {
                "event": "on_chat_model_stream",
                "name": "OpenAI",
                "data": {"chunk": MagicMock(content="Hello")},
            },
            {"event": "on_chain_end", "name": "LangGraph", "data": {"output": {}}},
        ]
        for e in events:
            yield e

    graph.astream_events = mock_events
    return graph


@pytest.mark.asyncio
async def test_chat_stream_success(mock_graph: MagicMock) -> None:
    """Test that /chat/stream yields valid Server-Sent Events (SSE)."""

    # Use dependency_overrides for EVERYTHING - cleaner and avoids signature mismatch
    services_override = {
        "_checkpointer": MagicMock(asetup=AsyncMock()),
        "_graph": mock_graph,
        "_telemetry": [],
    }

    app.dependency_overrides[get_services] = lambda: services_override
    app.dependency_overrides[get_orchestrator_graph] = lambda: mock_graph

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"query": "Hi", "user_id": "test", "session_id": "sess-1"}
        response = await ac.post("/v1/chat/stream", json=payload)

        assert response.status_code == 200  # noqa: PLR2004
        assert "text/event-stream" in response.headers["content-type"]
        assert "data: " in response.text
        assert "Hello" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_stream_error_handling(mock_graph: MagicMock) -> None:
    """Test that streaming handles node failures gracefully with an error event."""

    async def mock_events_fail(*args: Any, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        yield {"event": "metadata", "data": {"node": "detect_intent"}}
        raise Exception("Graph failure")

    mock_graph.astream_events = mock_events_fail

    services_override = {
        "_checkpointer": MagicMock(asetup=AsyncMock()),
        "_graph": mock_graph,
        "_telemetry": [],
    }

    app.dependency_overrides[get_services] = lambda: services_override
    app.dependency_overrides[get_orchestrator_graph] = lambda: mock_graph

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"query": "Fail", "user_id": "test", "session_id": "sess-2"}
        response = await ac.post("/v1/chat/stream", json=payload)
        assert response.status_code == 200  # noqa: PLR2004
        assert "event: error" in response.text

    app.dependency_overrides.clear()
