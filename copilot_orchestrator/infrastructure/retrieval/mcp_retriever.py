import logging
import re
from collections.abc import Mapping
from typing import Any

from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway

logger = logging.getLogger(__name__)


class MCPRetrieverGateway(RetrieverGateway):
    """An implementation of the retrieval gateway that connects to an MCP Server.

    Uses `mcp.client.session.ClientSession` to execute the `search_knowledge`
    tool provided by the data-layer-manager.
    """

    def __init__(self, mcp_client_session: Any) -> None:
        """Initialize with an active MCP Client session.

        Args:
            mcp_client_session: The active `mcp.client.session.ClientSession`
                (typed as Any to avoid hard dependency on mcp library internals
                in the signature, though it expects a valid session).
        """
        self.client_session = mcp_client_session

    async def retrieve(
        self, query: str, metadata: Mapping[str, Any] | None = None
    ) -> RetrievalResult:
        """Call the MCP tool to retrieve context."""
        logger.info(f"Delegating retrieval to MCP for query: '{query}'")

        try:
            # We call the 'search_knowledge' tool defined on the data-layer-manager MVP
            result = await self.client_session.call_tool(
                "search_knowledge", arguments={"query": query, "strategy": "hybrid"}
            )

            if not result or not hasattr(result, "content") or len(result.content) == 0:
                logger.warning("MCP tool returned empty or malformed result.")
                return RetrievalResult(
                    items=[], mode=RetrievalMode.HYBRID, metadata={"source": "mcp_retriever"}
                )

            # Extract the raw text from the TextContent object
            raw_text = result.content[0].text

            # If server returned the empty message directly
            if "No relevant knowledge found" in raw_text:
                return RetrievalResult(
                    items=[], mode=RetrievalMode.HYBRID, metadata={"source": "mcp_retriever"}
                )

            citations = self._parse_mcp_output(raw_text)

            return RetrievalResult(
                items=citations, mode=RetrievalMode.HYBRID, metadata={"source": "mcp_retriever"}
            )

        except Exception as e:
            logger.error(f"Failed to execute MCP retrieval tool: {e}", exc_info=True)
            # In case of failure (e.g. timeout, tool missing), return empty result.
            return RetrievalResult(
                items=[],
                mode=RetrievalMode.HYBRID,
                metadata={"source": "mcp_retriever", "error": str(e)},
            )

    def _parse_mcp_output(self, text: str) -> list[Citation]:
        """Parse the formatted string returned by data-layer-manager's search tool.

        Expected format of each block (separated by \n---\n):
        [1] Score: 0.9812 | Source: document.txt
        Content: The actual content here...
        """
        citations = []
        blocks = text.split("\n---\n")

        # Basic regex to pull out score, source, and everything after "Content: "
        pattern = re.compile(r"\[\d+\] Score: ([\d.]+) \| Source: (.*)\nContent: (.*)", re.DOTALL)

        for i, raw_block in enumerate(blocks, start=1):
            block = raw_block.strip()
            if not block:
                continue

            match = pattern.search(block)
            if match:
                score_str = match.group(1).strip()
                source = match.group(2).strip()
                content = match.group(3).strip()

                try:
                    score = float(score_str)
                except ValueError:
                    score = 0.0

                citations.append(
                    Citation(
                        source_id=f"mcp-result-{i}",
                        snippet=content,
                        source_title=source,
                        score=score,
                    )
                )
            else:
                # Fallback if the parsing fails for some reason
                citations.append(
                    Citation(
                        source_id=f"mcp-result-raw-{i}",
                        snippet=block,
                        source_title="MCP Search Result",
                        score=0.0,
                    )
                )

        return citations
