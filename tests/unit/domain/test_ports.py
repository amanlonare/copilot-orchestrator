from typing import Any

from copilot_orchestrator.domain.ports.llm_provider import LLMProvider
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway
from copilot_orchestrator.domain.ports.session_repository import SessionRepository


class MockLLM:
    async def generate(self, messages: Any) -> Any:
        return None


class MockRetriever:
    async def retrieve(self, query: str, metadata: dict[str, Any] | None = None) -> Any:
        return None


class MockRepo:
    async def load(self, session_id: str) -> Any:
        return None

    async def save(self, session: Any) -> None:
        pass


def test_llm_provider_protocol() -> None:
    mock = MockLLM()
    # verify protocol adherence using runtime_checkable
    assert isinstance(mock, LLMProvider)


def test_retriever_gateway_protocol() -> None:
    mock = MockRetriever()
    # verify protocol adherence using runtime_checkable
    assert isinstance(mock, RetrieverGateway)


def test_session_repository_protocol() -> None:
    mock = MockRepo()
    # verify protocol adherence using runtime_checkable
    assert isinstance(mock, SessionRepository)
