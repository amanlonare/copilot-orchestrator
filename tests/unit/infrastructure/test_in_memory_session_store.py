import pytest

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.infrastructure.sessions.in_memory_session_store import (
    InMemorySessionStore,
)


@pytest.mark.asyncio  # type: ignore[misc]
async def test_in_memory_session_store_save_and_load() -> None:
    # Arrange
    store = InMemorySessionStore()
    session = Session(session_id="s1")
    session.history.append(AgentMessage(role=MessageRole.USER, content="hello"))

    # Act
    await store.save(session)
    loaded = await store.load("s1")

    # Assert
    assert loaded is not None
    assert loaded.session_id == "s1"
    assert len(loaded.history) == 1
    assert loaded.history[0].content == "hello"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_in_memory_session_store_is_decoupled_by_deepcopy() -> None:
    # Arrange
    store = InMemorySessionStore()
    session = Session(session_id="s1")
    await store.save(session)

    # Act
    loaded = await store.load("s1")
    assert loaded is not None
    loaded.history.append(AgentMessage(role=MessageRole.USER, content="new"))

    # Check that original storage is not affected by local changes to loaded ref
    reloaded = await store.load("s1")
    assert reloaded is not None
    assert len(reloaded.history) == 0


@pytest.mark.asyncio  # type: ignore[misc]
async def test_in_memory_session_store_load_missing_returns_none() -> None:
    store = InMemorySessionStore()
    assert await store.load("missing") is None
