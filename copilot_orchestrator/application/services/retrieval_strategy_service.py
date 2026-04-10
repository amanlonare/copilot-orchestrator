import logging

from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway

logger = logging.getLogger(__name__)


class RetrievalStrategyService:
    """Service to determine and execute the context retrieval strategy."""

    def __init__(self, gateway: RetrieverGateway) -> None:
        """Initialize with a concrete retriever gateway.

        Args:
            gateway: Port for external context retrieval.
        """
        self._gateway = gateway

    def select_strategy(self, query: UserQuery) -> RetrievalMode:
        """Determine the best retrieval mode for the given query.

        Args:
            query: The processed user query.

        Returns:
            The recommended RetrievalMode.
        """
        logger.debug("Selecting retrieval strategy for: %s", query.text)
        # For MVP, we default to HYBRID.
        # Future logic: analyze query length, keywords, or intent to choose VECTOR/KEYWORD.
        return RetrievalMode.HYBRID

    async def retrieve_for_query(
        self, query: UserQuery, mode: RetrievalMode | None = None, top_k: int = 5
    ) -> RetrievalResult:
        """Execute retrieval based on the current strategy.

        Args:
            query: The processed user query.
            mode: Optional retrieval mode override.
            top_k: Number of results to retrieve.

        Returns:
            A RetrievalResult containing citations from knowledge bases.
        """
        target_mode = mode or self.select_strategy(query)
        logger.debug(
            "Executing retrieval for query: %s (mode=%s, top_k=%d)", query.text, target_mode, top_k
        )

        retrieval_metadata = {
            "mode": target_mode,
            "top_k": top_k,
            **(query.metadata or {}),
        }

        result = await self._gateway.retrieve(query=query.text, metadata=retrieval_metadata)

        logger.info(
            "Retrieval complete. Found %d items using %s mode in %.2fms",
            len(result.items),
            result.mode,
            result.latency_ms,
        )
        return result
