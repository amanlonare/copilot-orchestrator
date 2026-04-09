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

    async def retrieve_for_query(self, query: UserQuery, top_k: int = 5) -> RetrievalResult:
        """Execute retrieval based on the current strategy.

        Args:
            query: The processed user query.
            top_k: Number of results to retrieve.

        Returns:
            A RetrievalResult containing citations from knowledge bases.
        """
        logger.debug("Executing retrieval for query: %s (top_k=%d)", query.text, top_k)

        # In a real implementation, we might choose the mode based on the query or intent.
        # For now, we default to HYBRID as per the phase plan.
        retrieval_metadata = {
            "mode": RetrievalMode.HYBRID,
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
