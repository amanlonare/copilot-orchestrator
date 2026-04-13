from collections.abc import Mapping
from typing import Any

from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway


class MockRetrieverGateway(RetrieverGateway):
    """A mock implementation of the retrieval gateway for Phase 6 MVP.

    Returns canned responses based on keyword matching to demonstrate
    the end-to-end orchestration flow without a live data layer.
    """

    async def retrieve(
        self, query: str, metadata: Mapping[str, Any] | None = None
    ) -> RetrievalResult:
        """Simulate a retrieval operation."""
        query_lower = query.lower()

        items = []
        if "france" in query_lower:
            items.append(
                Citation(
                    source_id="mock-1",
                    snippet="The capital of France is Paris. It is known as the City of Light.",
                    source_title="European Capitals",
                    score=0.95,
                )
            )
        elif "langgraph" in query_lower:
            items.append(
                Citation(
                    source_id="mock-2",
                    snippet=(
                        "LangGraph is a library for building stateful, "
                        "multi-actor applications with LLMs."
                    ),
                    source_title="Technical Documentation",
                    score=0.98,
                )
            )

        return RetrievalResult(
            items=items, mode=RetrievalMode.HYBRID, metadata={"source": "mock_retriever_gateway"}
        )
