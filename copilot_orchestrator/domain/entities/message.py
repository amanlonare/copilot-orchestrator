from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.enums.message_role import MessageRole


@dataclass(slots=True)
class AgentMessage:
    """A single turn in the interaction history.

    Attributes:
        role: The persona originating the message (USER, ASSISTANT, etc.).
        content: The text content of the message.
        citations: Optional references to source materials.
        name: Internal name of the actor (e.g., tool name).
        metadata: Extra structured data for tracing or frontend features.
    """

    role: MessageRole
    content: str
    citations: list[Citation] = field(default_factory=list)
    name: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
