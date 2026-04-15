from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

from copilot_orchestrator.domain.entities.message import AgentMessage


@runtime_checkable
class LLMProvider(Protocol):
    """Contract for Large Language Model interactions.

    Implementations of this protocol (e.g., OpenAI, Azure OpenAI, Anthropic)
    must provide a thread-safe async generation interface.
    """

    async def generate(
        self, messages: list[AgentMessage], tools: list[type] | None = None
    ) -> AgentMessage:
        """Generate a response based on the provided conversation context.

        Args:
            messages: Full list of turns in the current context window.
            tools: Optional list of Pydantic models to use as tools.

        Returns:
            The generated message from the model (may contain tool_calls).
        """
        ...

    async def generate_structured(self, messages: list[AgentMessage], response_model: type) -> Any:
        """Generate a structured response parsed into a specific Pydantic model.

        Args:
            messages: Conversation history.
            response_model: The Pydantic class to use for structured parsing.

        Returns:
            An instance of the specified response_model.
        """
        ...

    def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]:
        """Stream the generated response content as an async iterator of chunks.

        This method should be implemented as an async generator using 'yield'.

        Args:
            messages: Full conversation history to send to the model.

        Yields:
            Token chunks (strings) from the model's response.
        """
        ...
