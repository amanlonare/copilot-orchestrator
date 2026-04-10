from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from copilot_orchestrator.application.services.context_builder_service import ContextBuilderService
from copilot_orchestrator.application.services.fallback_service import FallbackService
from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.application.services.query_intake_service import QueryIntakeService
from copilot_orchestrator.application.services.retrieval_strategy_service import (
    RetrievalStrategyService,
)
from copilot_orchestrator.application.services.session_service import SessionService
from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.query import OrchestratorRequest, UserQuery
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.orchestration.graph import orchestrator_graph


@pytest.fixture
def mock_llm_provider() -> MagicMock:
    provider = MagicMock()
    provider.generate = AsyncMock()
    return provider


@pytest.fixture
def mock_retriever_gateway() -> MagicMock:
    gateway = MagicMock()
    gateway.retrieve = AsyncMock()
    return gateway


@pytest.fixture
def mock_session_repository() -> MagicMock:
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.load = AsyncMock()
    return repo


@pytest.fixture
def services(
    mock_llm_provider: MagicMock,
    mock_retriever_gateway: MagicMock,
    mock_session_repository: MagicMock,
) -> dict[str, Any]:
    return {
        "query_intake_service": QueryIntakeService(),
        "retrieval_strategy_service": RetrievalStrategyService(mock_retriever_gateway),
        "context_builder_service": ContextBuilderService(),
        "generation_service": GenerationService(mock_llm_provider),
        "session_service": SessionService(mock_session_repository),
        "fallback_service": FallbackService(),
    }


@pytest.mark.asyncio
async def test_graph_happy_path(
    services: dict[str, Any], mock_llm_provider: MagicMock, mock_retriever_gateway: MagicMock
) -> None:
    """Test full successful orchestration flow."""
    # 1. Setup Mocks
    mock_retriever_gateway.retrieve.return_value = RetrievalResult(
        items=[
            Citation(
                source_id="src-1",
                snippet="The capital of France is Paris.",
                source_title="Geography",
                score=0.9,
            )
        ],
        mode=RetrievalMode.HYBRID,
    )
    mock_llm_provider.generate.return_value = AgentMessage(
        role=MessageRole.ASSISTANT, content="The capital of France is Paris."
    )

    # 2. Input
    initial_request = OrchestratorRequest(
        query=UserQuery(text="What is the capital of France?", session_id="test-session")
    )
    initial_state = {
        "request": initial_request,
        "session": Session(session_id="test-session"),
        "errors": [],
        "warnings": [],
    }

    # 3. Execute
    config = {"configurable": services}
    final_state = await orchestrator_graph.ainvoke(initial_state, config=config)

    # 4. Assertions
    assert final_state["normalized_query"].text == "What is the capital of France?"
    assert final_state["retrieved_result"].items[0].snippet == "The capital of France is Paris."
    assert "Paris" in final_state["assembled_context"]
    assert final_state["answer"].content == "The capital of France is Paris."
    assert final_state.get("fallback_flag", False) is False
    assert len(final_state["session"].history) == 1
    assert final_state["session"].history[0].content == "The capital of France is Paris."


@pytest.mark.asyncio
async def test_graph_fallback_path(
    services: dict[str, Any], mock_llm_provider: MagicMock, mock_retriever_gateway: MagicMock
) -> None:
    """Test orchestration flow when retrieval returns no relevant context."""
    # 1. Setup Mocks (Empty retrieval)
    mock_retriever_gateway.retrieve.return_value = RetrievalResult(
        items=[], mode=RetrievalMode.HYBRID
    )

    # 2. Input
    initial_request = OrchestratorRequest(
        query=UserQuery(text="Unknown topic", session_id="test-session")
    )
    initial_state = {
        "request": initial_request,
        "session": Session(session_id="test-session"),
        "errors": [],
        "warnings": [],
    }

    # 3. Execute
    config = {"configurable": services}
    final_state = await orchestrator_graph.ainvoke(initial_state, config=config)

    # 4. Assertions
    assert final_state["fallback_flag"] is True
    assert "couldn't find specific information" in final_state["answer"].content
    # LLM should not have been called for generation if fallback was triggered
    mock_llm_provider.generate.assert_not_called()
    assert len(final_state["session"].history) == 1
