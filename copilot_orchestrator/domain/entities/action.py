from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from copilot_orchestrator.domain.enums.action_type import ActionType


@dataclass(slots=True)
class Action:
    """A tool invocation or system action proposed by the agent.

    Attributes:
        type: Category of action (e.g., SEARCH, EMAIL).
        label: Human-readable description of the action.
        target: Optional recipient or target entity.
        parameters: Configuration or arguments for the action.
        confidence: Probability the action is appropriate for the query.
    """

    type: ActionType
    label: str
    target: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    confidence: float | None = None
