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
from copilot_orchestrator.application.use_cases.run_orchestrator import RunOrchestratorUseCase
from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode


@pytest.fixture  # type: ignore[misc]
def mock_services() -> dict[str, Any]:
    return {
        "intake": MagicMock(spec=QueryIntakeService),
        "session": MagicMock(spec=SessionService),
        "retrieval": MagicMock(spec=RetrievalStrategyService),
        "context": MagicMock(spec=ContextBuilderService),
        "generation": MagicMock(spec=GenerationService),
        "fallback": MagicMock(spec=FallbackService),
    }


@pytest.mark.asyncio  # type: ignore[misc]
async def test_run_orchestrator_success(mock_services: dict[str, Any]) -> None:
    # 1. Setup mocks
    query = UserQuery(text="hello", session_id="s1")
    session = Session(session_id="s1")
    retrieval_result = RetrievalResult(items=[], mode=RetrievalMode.HYBRID)
    agent_message = AgentMessage(content="World", role=MessageRole.ASSISTANT)

    mock_services["intake"].process.return_value = query
    mock_services["session"].load_session = AsyncMock(return_value=session)
    mock_services["retrieval"].retrieve_for_query = AsyncMock(return_value=retrieval_result)
    mock_services["fallback"].evaluate_fallback.return_value = False
    mock_services["context"].build_context.return_value = "Mocked Context"
    mock_services["generation"].generate_answer = AsyncMock(return_value=agent_message)
    mock_services["session"].append_and_save = AsyncMock()

    # 2. Instantiate and execute
    use_case = RunOrchestratorUseCase(
        intake_service=mock_services["intake"],
        session_service=mock_services["session"],
        retrieval_service=mock_services["retrieval"],
        context_service=mock_services["context"],
        generation_service=mock_services["generation"],
        fallback_service=mock_services["fallback"],
    )

    result = await use_case.execute(session_id="s1", raw_query="hello")

    # 3. Assertions
    assert result.answer == "World"
    assert result.fallback is False
    assert result.metadata["session_id"] == "s1"

    # Verify sequential collaboration
    mock_services["intake"].process.assert_called_once()
    mock_services["session"].load_session.assert_called_once_with("s1")
    mock_services["retrieval"].retrieve_for_query.assert_called_once_with(query)
    mock_services["fallback"].evaluate_fallback.assert_called_once_with(retrieval_result.items)
    mock_services["context"].build_context.assert_called_once_with(retrieval_result.items)
    mock_services["generation"].generate_answer.assert_called_once_with(
        context="Mocked Context", query=query, session=session
    )
    mock_services["session"].append_and_save.assert_called_once_with(session, agent_message)
