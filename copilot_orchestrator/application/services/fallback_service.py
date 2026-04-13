import logging

from copilot_orchestrator.core.config import settings
from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.enums.message_role import MessageRole

logger = logging.getLogger(__name__)


class FallbackService:
    """Service to decide if a response should be generic or grounded."""

    def evaluate_fallback(self, citations: list[Citation], min_score: float | None = None) -> bool:
        """Analyze citations to decide if fallback is necessary.

        Args:
            citations: The list of source nuggets found.
            min_score: Minimum relevance score required to avoid fallback.

        Returns:
            True if fallback should be triggered, False otherwise.
        """

        config_threshold = settings.RAG_RELEVANCE_THRESHOLD
        threshold = min_score if min_score is not None else config_threshold

        logger.debug(
            "Evaluating fallback for %d citations (Threshold: %.2f)", len(citations), threshold
        )

        if not citations:
            logger.info("No citations found. Triggering fallback.")
            return True

        # Check for any citation with a score above the threshold
        # (Assuming score is 0.0 to 1.0)
        max_score = max((c.score or 0.0 for c in citations), default=0.0)

        if max_score < threshold:
            logger.info(
                "Max score (%.2f) below threshold (%.2f). Triggering fallback.",
                max_score,
                threshold,
            )
            return True

        logger.info("Found sufficient context with max score %.2f. No fallback.", max_score)
        return False

    def generate_fallback_response(self, query: UserQuery) -> AgentMessage:
        """Generate a polite fallback response when context is missing.

        Args:
            query: The user's target query.

        Returns:
            An AgentMessage with the fallback content.
        """
        logger.info("Generating fallback response for session: %s", query.session_id)
        content = (
            "I'm sorry, but I couldn't find specific information in the available knowledge "
            "to answer your question accurately. Please try rephrasing your request or "
            "contact support if the issue persists."
        )
        return AgentMessage(
            role=MessageRole.ASSISTANT, content=content, metadata={"fallback": True}
        )
