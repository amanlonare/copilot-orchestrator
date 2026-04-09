from datetime import datetime

from copilot_orchestrator.domain.entities.action import Action
from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.retrieval_result import IntentResult
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.entities.token_usage import TokenUsage
from copilot_orchestrator.domain.enums.action_type import ActionType
from copilot_orchestrator.domain.enums.intent_type import IntentType
from copilot_orchestrator.domain.enums.message_role import MessageRole


def test_token_usage_addition() -> None:
    usage1 = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    usage2 = TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)

    total = usage1.add(usage2)

    expected_prompt = 30
    expected_completion = 15
    expected_total = 45
    assert total.prompt_tokens == expected_prompt
    assert total.completion_tokens == expected_completion
    assert total.total_tokens == expected_total


def test_session_initialization() -> None:
    session = Session(session_id="test-session")

    assert session.session_id == "test-session"
    assert session.history == []
    assert isinstance(session.usage, TokenUsage)
    assert isinstance(session.created_at, datetime)
    assert isinstance(session.updated_at, datetime)


def test_agent_message_with_defaults() -> None:
    msg = AgentMessage(role=MessageRole.USER, content="hello")

    assert msg.role == MessageRole.USER
    assert msg.content == "hello"
    assert msg.citations == []
    assert msg.metadata == {}


def test_action_with_enum() -> None:
    action = Action(type=ActionType.SEARCH, label="Search Web")
    assert action.type == ActionType.SEARCH
    assert action.label == "Search Web"


def test_intent_result_with_enum() -> None:
    confidence_val = 0.9
    intent = IntentResult(intent=IntentType.KNOWLEDGE, confidence=confidence_val)
    assert intent.intent == IntentType.KNOWLEDGE
    assert intent.confidence == confidence_val
