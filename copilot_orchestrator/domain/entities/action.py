from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from copilot_orchestrator.domain.enums.action_domain import ActionDomain
from copilot_orchestrator.domain.enums.action_type import ActionType


@dataclass(slots=True)
class Action:
    """A tool invocation or system action proposed by the agent.

    Attributes:
        type: Category of action (e.g., SEARCH, EMAIL or specialized domain types).
        label: Human-readable description of the action.
        domain: The business domain this action belongs to (e.g., ECOMMERCE).
        target: Optional recipient or target entity.
        parameters: Configuration or arguments for the action.
        metadata: Additional context for history, auditing, or system-specific needs.
        confidence: Probability the action is appropriate for the query.
    """

    type: ActionType | str
    label: str
    domain: ActionDomain | None = None
    target: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    confidence: float | None = None
