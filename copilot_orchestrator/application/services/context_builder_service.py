import logging

from copilot_orchestrator.domain.entities.citation import Citation

logger = logging.getLogger(__name__)


class ContextBuilderService:
    """Service to transform raw citations into a prompt-ready context string."""

    def build_context(self, citations: list[Citation]) -> str:
        """Process and format citations into a context block.

        Args:
            citations: List of source nuggets retrieved for the query.

        Returns:
            A single string containing formatted, deduplicated snippets.
        """
        logger.debug("Building context from %d citations", len(citations))

        if not citations:
            logger.info("No citations provided; returning empty context.")
            return ""

        # Simple deduplication based on snippet content
        seen_snippets = set()
        unique_citations = []
        for citation in citations:
            if citation.snippet not in seen_snippets:
                seen_snippets.add(citation.snippet)
                unique_citations.append(citation)

        # Basic formatting: [Index] Title: Snippet
        context_blocks = []
        for i, citation in enumerate(unique_citations, 1):
            title = citation.source_title or "Unknown Source"
            block = f"[{i}] {title}\n{citation.snippet}"
            context_blocks.append(block)

        formatted_context = "\n\n".join(context_blocks)

        logger.info(
            "Context assembled. Original: %d, Unique: %d, Length: %d chars",
            len(citations),
            len(unique_citations),
            len(formatted_context),
        )
        return formatted_context
