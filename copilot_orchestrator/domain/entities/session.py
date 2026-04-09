from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.token_usage import TokenUsage


@dataclass(slots=True)
class Session:
    """A durable conversation record between a user and the agent.

    Attributes:
        session_id: Unique identifier for the conversation.
        history: Sequence of messages exchanged in this session.
        usage: Aggregated token consumption for the session.
        metadata: Session-level flags, preferences, or technical context.
        created_at: ISO timestamp of session creation.
        updated_at: ISO timestamp of the last message or state change.
    """

    session_id: str
    history: list[AgentMessage] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
