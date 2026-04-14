from typing import Any, Protocol, runtime_checkable

from copilot_orchestrator.domain.entities.action import Action


@runtime_checkable
class ActionHandler(Protocol):
    """Protocol for domain-specific action execution handlers.

    Handlers translate business actions into specific tool calls
    using appropriate infrastructure clients.
    """

    async def execute(self, action: Action) -> list[dict[str, Any]]:
        """Execute the given action and return a list of tool results.

        Args:
            action: The resolved action with parameters and domain context.

        Returns:
            A list of dictionary objects representing tool outputs.
        """
        ...
