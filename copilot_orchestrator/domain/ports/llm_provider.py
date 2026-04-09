from typing import Protocol, runtime_checkable

from copilot_orchestrator.domain.entities.message import AgentMessage


@runtime_checkable
class LLMProvider(Protocol):
    """Contract for Large Language Model interactions.

    Implementations of this protocol (e.g., OpenAI, Azure OpenAI, Anthropic)
    must provide a thread-safe async generation interface.
    """

    async def generate(self, messages: list[AgentMessage]) -> AgentMessage:
        """Generate a response based on the provided conversation context.

        Args:
            messages: Full list of turns in the current context window.

        Returns:
            The generated message from the model.
        """
        ...
