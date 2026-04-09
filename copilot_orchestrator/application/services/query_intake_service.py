import logging
from collections.abc import Mapping
from typing import Any

from copilot_orchestrator.domain.entities.query import UserQuery

logger = logging.getLogger(__name__)


class QueryIntakeService:
    """Service responsible for cleaning and validating incoming user queries."""

    def process(
        self,
        raw_query: str,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> UserQuery:
        """Process raw input into a structured UserQuery entity.

        Args:
            raw_query: The raw string from the user.
            session_id: Optional context identifier.
            user_id: Optional user identifier.
            metadata: Extra contextual data.

        Returns:
            A validated UserQuery entity.

        Raises:
            ValueError: If the query is empty or only whitespace.
        """
        logger.debug("Processing raw query: %s", raw_query)

        trimmed_query = raw_query.strip()
        if not trimmed_query:
            logger.warning("Empty query received.")
            raise ValueError("Query cannot be empty.")

        query = UserQuery(
            text=trimmed_query, session_id=session_id, user_id=user_id, metadata=metadata or {}
        )

        logger.info("Query intake successful for session: %s", session_id)
        return query
