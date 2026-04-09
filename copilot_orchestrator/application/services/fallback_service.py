import logging

from copilot_orchestrator.domain.entities.citation import Citation

logger = logging.getLogger(__name__)


class FallbackService:
    """Service to decide if a response should be generic or grounded."""

    def evaluate_fallback(self, citations: list[Citation], min_score: float = 0.5) -> bool:
        """Analyze citations to decide if fallback is necessary.

        Args:
            citations: The list of source nuggets found.
            min_score: Minimum relevance score required to avoid fallback.

        Returns:
            True if fallback should be triggered, False otherwise.
        """
        logger.debug("Evaluating fallback for %d citations", len(citations))

        if not citations:
            logger.info("No citations found. Triggering fallback.")
            return True

        # Check for any citation with a score above the threshold
        # (Assuming score is 0.0 to 1.0)
        max_score = max((c.score or 0.0 for c in citations), default=0.0)

        if max_score < min_score:
            logger.info(
                "Max score (%.2f) below threshold (%.2f). Triggering fallback.",
                max_score,
                min_score,
            )
            return True

        logger.info("Found sufficient context with max score %.2f. No fallback.", max_score)
        return False
