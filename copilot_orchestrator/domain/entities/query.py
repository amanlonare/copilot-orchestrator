from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from copilot_orchestrator.domain.entities.message import AgentMessage


@dataclass(slots=True)
class UserQuery:
    """The raw incoming request from a user.

    Attributes:
        text: The user's input string.
        user_id: Unique identifier for the person sending the prompt.
        session_id: Identifier for the conversation context.
        metadata: Extra structured data (e.g., location, device).
    """

    text: str
    user_id: str | None = None
    session_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrchestratorRequest:
    """The enriched request prepared for the internal orchestration graph.

    Attributes:
        query: UserQuery: The original input from the user.
        history: list[AgentMessage]: Previous conversation turns in this session.
        metadata: Mapping[str, Any]: Specific graph-level runtime flags or context.
    """

    query: UserQuery
    history: list[AgentMessage] = field(default_factory=list)
    metadata: Mapping[str, Any] = field(default_factory=dict)
