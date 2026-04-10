from unittest.mock import AsyncMock, MagicMock

import pytest

from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.infrastructure.retrieval.mcp_retriever import MCPRetrieverGateway


@pytest.fixture
def mock_mcp_session() -> AsyncMock:
    """Returns a completely mocked MCP client session."""
    session = AsyncMock()
    return session


@pytest.fixture
def mcp_retriever(mock_mcp_session: AsyncMock) -> MCPRetrieverGateway:
    return MCPRetrieverGateway(mcp_client_session=mock_mcp_session)


@pytest.mark.asyncio
async def test_mcp_retriever_successful_call_with_results(
    mcp_retriever: MCPRetrieverGateway, mock_mcp_session: AsyncMock
) -> None:
    # Mocking the content returned by from the MCP TextContent model
    mock_content = MagicMock()
    # Provide the formatted response block similar to data_layer_manager
    mock_content.text = (
        "[1] Score: 0.9500 | Source: file1.txt\n"
        "Content: Snippet 1\n"
        "---\n"
        "[2] Score: 0.8200 | Source: file2.txt\n"
        "Content: Snippet 2\n"
    )

    mock_result = MagicMock()
    mock_result.content = [mock_content]
    mock_mcp_session.call_tool.return_value = mock_result

    # Call the retriever
    retrieval_result = await mcp_retriever.retrieve("my test query")

    # Verify tool was called correctly
    mock_mcp_session.call_tool.assert_called_once_with(
        "search_knowledge", arguments={"query": "my test query", "strategy": "hybrid"}
    )

    # Verify parsing into Citation objects
    assert retrieval_result.mode == RetrievalMode.HYBRID
    assert len(retrieval_result.items) == 2  # noqa: PLR2004

    cit1 = retrieval_result.items[0]
    assert cit1.source_title == "file1.txt"
    assert cit1.score == 0.95  # noqa: PLR2004
    assert cit1.snippet == "Snippet 1"

    cit2 = retrieval_result.items[1]
    assert cit2.source_title == "file2.txt"
    assert cit2.score == 0.82  # noqa: PLR2004
    assert cit2.snippet == "Snippet 2"


@pytest.mark.asyncio
async def test_mcp_retriever_no_results_string(
    mcp_retriever: MCPRetrieverGateway, mock_mcp_session: AsyncMock
) -> None:
    # Mocking the specific "No relevant knowledge found" string the server might return
    mock_content = MagicMock()
    mock_content.text = "No relevant knowledge found for the given query and strategy."

    mock_result = MagicMock()
    mock_result.content = [mock_content]
    mock_mcp_session.call_tool.return_value = mock_result

    retrieval_result = await mcp_retriever.retrieve("my test query")

    assert len(retrieval_result.items) == 0


@pytest.mark.asyncio
async def test_mcp_retriever_empty_content(
    mcp_retriever: MCPRetrieverGateway, mock_mcp_session: AsyncMock
) -> None:
    # Returning empty content list
    mock_result = MagicMock()
    mock_result.content = []
    mock_mcp_session.call_tool.return_value = mock_result

    retrieval_result = await mcp_retriever.retrieve("my test query")

    assert len(retrieval_result.items) == 0


@pytest.mark.asyncio
async def test_mcp_retriever_client_exception(
    mcp_retriever: MCPRetrieverGateway, mock_mcp_session: AsyncMock
) -> None:
    # Simulating connection error or timeout
    mock_mcp_session.call_tool.side_effect = Exception("Connection Refused")

    retrieval_result = await mcp_retriever.retrieve("my test query")

    # Should safely catch exception and return empty result
    assert len(retrieval_result.items) == 0
    assert retrieval_result.metadata["error"] == "Connection Refused"
