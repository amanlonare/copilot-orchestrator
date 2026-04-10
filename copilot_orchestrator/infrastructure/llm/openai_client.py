from openai import AsyncOpenAI

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.ports.llm_provider import LLMProvider


class OpenAIClient(LLMProvider):
    """Infrastructure adapter for OpenAI Chat Completions API.

    This client implements the LLMProvider port, translating between
    domain entities and the OpenAI SDK format.
    """

    def __init__(self, async_client: AsyncOpenAI, model: str = "gpt-4o-mini"):
        """Initialize the client with an authenticated AsyncOpenAI instance.

        Args:
            async_client: Pre-configured OpenAI client.
            model: The model identifier to use for generations.
        """
        self._client = async_client
        self._model = model

    async def generate(self, messages: list[AgentMessage]) -> AgentMessage:
        """Generate a completion using OpenAI.

        Args:
            messages: Conversation history to send to the model.

        Returns:
            A new message entity containing the model's response.
        """
        # Translate domain messages to OpenAI schema
        openai_messages = []
        for msg in messages:
            open_msg = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                open_msg["name"] = msg.name
            openai_messages.append(open_msg)

        # Call the provider
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=openai_messages,
        )

        # Map back to domain
        content = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        return AgentMessage(
            role=MessageRole.ASSISTANT,
            content=content,
            metadata={"model": self._model, "usage": usage},
        )
