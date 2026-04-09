import logging

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.ports.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class GenerationService:
    """Service to orchestrate grounded response generation using an LLM."""

    def __init__(self, provider: LLMProvider) -> None:
        """Initialize with a concrete LLM provider.

        Args:
            provider: Port for LLM interactions.
        """
        self._provider = provider

    async def generate_answer(
        self, context: str, query: UserQuery, session: Session
    ) -> AgentMessage:
        """Generate a response grounded in the provided context.

        Args:
            context: The text context retrieved for the query.
            query: The user's target query.
            session: The contemporary conversation session.

        Returns:
            An AgentMessage containing the generated response.
        """
        logger.debug("Generating answer for query: %s", query.text)

        # 1. Prepare messages list starting with System Prompt containing context
        system_content = (
            "You are a helpful and professional assistant. "
            "Use the following context to answer the user's question. "
            "If the context doesn't contain the answer, "
            "say you don't know based on the context.\n\n"
            f"Context:\n{context}"
        )

        messages = [AgentMessage(role=MessageRole.SYSTEM, content=system_content)]

        # 2. Add history (avoiding duplicating messages if they are already in session)
        messages.extend(session.history)

        # 3. Add latest user query
        messages.append(AgentMessage(role=MessageRole.USER, content=query.text))

        logger.info("Calling LLM provider with %d messages", len(messages))

        response = await self._provider.generate(messages)

        logger.info("Response generated successfully. Length: %d chars", len(response.content))
        return response
