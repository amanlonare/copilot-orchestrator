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
from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.domain.ports.llm_provider import LLMProvider
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway
from copilot_orchestrator.domain.ports.session_repository import SessionRepository

# --- QueryIntakeService Tests ---


def test_query_intake_trims_whitespace() -> None:
    service = QueryIntakeService()
    raw_query = "  Hello  World  "
    query = service.process(raw_query)
    assert query.text == "Hello  World"


def test_query_intake_raises_value_error_for_empty_query() -> None:
    service = QueryIntakeService()
    with pytest.raises(ValueError, match=r"Query cannot be empty\."):
        service.process("   ")


def test_query_intake_assigns_metadata() -> None:
    service = QueryIntakeService()
    metadata = {"source": "web", "ip": "127.0.0.1"}
    query = service.process("test query", metadata=metadata)
    assert query.metadata == metadata


def test_query_intake_assigns_session_and_user_id() -> None:
    service = QueryIntakeService()
    query = service.process("test", session_id="s123", user_id="u456")
    assert query.session_id == "s123"
    assert query.user_id == "u456"


# --- SessionService Tests ---


# First asyncio test also needs it
@pytest.mark.asyncio
async def test_session_service_loads_new_session_if_not_found() -> None:
    repo = MagicMock(spec=SessionRepository)
    repo.load = AsyncMock(return_value=None)
    service = SessionService(repo)

    session = await service.load_session("new_id")
    assert isinstance(session, Session)
    assert session.session_id == "new_id"
    assert len(session.history) == 0


@pytest.mark.asyncio
async def test_session_service_loads_existing_session() -> None:
    existing_session = Session(session_id="ex123")
    repo = MagicMock(spec=SessionRepository)
    repo.load = AsyncMock(return_value=existing_session)
    service = SessionService(repo)

    session = await service.load_session("ex123")
    assert session is existing_session


@pytest.mark.asyncio
async def test_session_service_appends_and_saves() -> None:
    session = Session(session_id="s1")
    repo = MagicMock(spec=SessionRepository)
    repo.save = AsyncMock()
    service = SessionService(repo)

    message = AgentMessage(content="hello", role=MessageRole.USER)
    await service.append_and_save(session, message)

    assert len(session.history) == 1
    assert session.history[0] == message
    repo.save.assert_called_once_with(session)


# --- RetrievalStrategyService Tests ---


@pytest.mark.asyncio
async def test_retrieval_strategy_queries_gateway() -> None:
    gateway = MagicMock(spec=RetrieverGateway)
    mock_result = RetrievalResult(items=[], mode=RetrievalMode.HYBRID)
    gateway.retrieve = AsyncMock(return_value=mock_result)

    service = RetrievalStrategyService(gateway)
    query = UserQuery(text="how to build agents")

    result = await service.retrieve_for_query(query)

    assert result == mock_result
    gateway.retrieve.assert_called_once()
    _, kwargs = gateway.retrieve.call_args
    assert kwargs["query"] == "how to build agents"
    assert kwargs["metadata"]["mode"] == RetrievalMode.HYBRID


# --- ContextBuilderService Tests ---


def test_context_builder_deduplicates_snippets() -> None:
    service = ContextBuilderService()
    citations = [
        Citation(source_id="1", snippet="A", source_title="S1"),
        Citation(source_id="2", snippet="A", source_title="S2"),  # Duplicate snippet
        Citation(source_id="3", snippet="B", source_title="S3"),
    ]

    context = service.build_context(citations)
    assert "[1] S1\nA" in context
    assert "[2] S3\nB" in context
    assert "[3]" not in context  # Should only have 2 blocks


def test_context_builder_handles_empty_list() -> None:
    service = ContextBuilderService()
    assert service.build_context([]) == ""


# --- GenerationService Tests ---


@pytest.mark.asyncio
async def test_generation_service_calls_provider() -> None:
    provider = MagicMock(spec=LLMProvider)
    mock_response = AgentMessage(content="World", role=MessageRole.ASSISTANT)
    provider.generate = AsyncMock(return_value=mock_response)

    service = GenerationService(provider)
    query = UserQuery(text="Hello")
    session = Session(session_id="s1")

    response = await service.generate_answer("Some context", query, session)

    expected_msg_count = 2
    assert response == mock_response
    provider.generate.assert_called_once()
    args, _ = provider.generate.call_args
    messages = args[0]
    assert len(messages) == expected_msg_count  # System + User (No history in this case)
    assert messages[0].role == MessageRole.SYSTEM
    assert "Some context" in messages[0].content
    assert messages[1].role == MessageRole.USER
    assert messages[1].content == "Hello"


# --- FallbackService Tests ---


def test_fallback_service_returns_true_for_no_citations() -> None:
    service = FallbackService()
    assert service.evaluate_fallback([]) is True


def test_fallback_service_returns_true_for_low_scores() -> None:
    service = FallbackService()
    citations = [
        Citation(source_id="1", snippet="A", score=0.2),
        Citation(source_id="2", snippet="B", score=0.4),
    ]
    assert service.evaluate_fallback(citations, min_score=0.5) is True


def test_fallback_service_returns_false_for_high_scores() -> None:
    service = FallbackService()
    citations = [
        Citation(source_id="1", snippet="A", score=0.2),
        Citation(source_id="2", snippet="B", score=0.8),
    ]
    assert service.evaluate_fallback(citations, min_score=0.5) is False
