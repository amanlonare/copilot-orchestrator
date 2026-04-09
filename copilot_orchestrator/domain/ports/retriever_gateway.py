from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult


@runtime_checkable
class RetrieverGateway(Protocol):
    """Contract for external context retrieval from knowledge bases.

    Implementations (e.g., Pinecone, Weaviate, or internal APIs) should
    provide low-latency similarity search.
    """

    async def retrieve(
        self, query: str, metadata: Mapping[str, Any] | None = None
    ) -> RetrievalResult:
        """Retrieve relevant context for the given query.

        Args:
            query: The search term or internal query to retrieve for.
            metadata: Optional filters or tenant-specific context.

        Returns:
            A RetrievalResult containing citation chunks and metadata.
        """
        ...
