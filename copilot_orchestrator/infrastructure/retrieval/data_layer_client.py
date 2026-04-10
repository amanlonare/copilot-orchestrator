from collections.abc import Mapping
from typing import Any

import httpx

from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway


class DataLayerClient(RetrieverGateway):
    """Infrastructure adapter for talking to the external data layer.

    This client implements the RetrieverGateway port using HTTPX to
    call search services and map their responses into domain RetrievalResults.
    """

    def __init__(self, base_url: str, api_key: str | None = None, timeout_seconds: float = 10.0):
        """Initialize the client with connection details.

        Args:
            base_url: The root endpoint of the retrieval service.
            api_key: Optional secret for authorization.
            timeout_seconds: Request timeout for retrieval calls.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._headers = {"Content-Type": "application/json"}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    async def retrieve(
        self, query: str, metadata: Mapping[str, Any] | None = None
    ) -> RetrievalResult:
        """Retrieve context via the external API.

        Args:
            query: The text to search for.
            metadata: Extra filters (e.g., retrieval mode, top_k).

        Returns:
            A populated RetrievalResult domain object.
        """
        params = {
            "q": query,
            "mode": (metadata or {}).get("mode", RetrievalMode.HYBRID),
            "limit": (metadata or {}).get("top_k", 5),
        }

        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as client:
            try:
                # This assumes a hypothetical external endpoint layout.
                # In a real environment, this would mirror the data-layer's contract.
                response = await client.get(f"{self._base_url}/search", params=params)
                response.raise_for_status()
                data = response.json()

                citations = [
                    Citation(
                        source_id=item["id"],
                        source_title=item.get("title", "Unknown"),
                        snippet=item["text"],
                        score=item.get("relevance", 0.0),
                        metadata=item.get("metadata", {}),
                    )
                    for item in data.get("results", [])
                ]

                return RetrievalResult(
                    items=citations,
                    mode=RetrievalMode(data.get("mode", params["mode"])),
                    latency_ms=response.elapsed.total_seconds() * 1000,
                    metadata={"provider_id": data.get("provider")},
                )
            except (httpx.HTTPError, KeyError, ValueError) as e:
                # For MVP, we return an empty result on failure to keep the orchestrator resilient,
                # but in production, we might raise a custom InfrastructureException.
                return RetrievalResult(
                    items=[],
                    metadata={"error": str(e)},
                )
