from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.infrastructure.retrieval.data_layer_client import DataLayerClient


@pytest.mark.asyncio  # type: ignore[misc]
async def test_data_layer_client_retrieve_success() -> None:
    # Arrange
    base_url = "https://api.test"
    client = DataLayerClient(base_url=base_url, api_key="secret")

    mock_data = {
        "results": [
            {"id": "c1", "title": "Doc 1", "text": "Content A", "relevance": 0.9},
            {"id": "c2", "text": "Content B"},
        ],
        "mode": "hybrid",
        "provider": "test-provider",
    }

    # Mock the response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data
    mock_response.raise_for_status = MagicMock()
    mock_response.elapsed = MagicMock()
    mock_response.elapsed.total_seconds.return_value = 0.5

    # Mock the AsyncClient behavior (__aenter__, get, etc.)
    with patch("httpx.AsyncClient", autospec=True) as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.get = AsyncMock(return_value=mock_response)

        # Act
        expected_items = 2
        result = await client.retrieve("test query", metadata={"top_k": expected_items})

        # Assert
        assert len(result.items) == expected_items
        expected_score = 0.9
        assert result.items[0].source_id == "c1"
        assert result.items[0].source_title == "Doc 1"
        assert result.items[0].score == expected_score
        assert result.items[1].source_title == "Unknown"
        assert result.mode == RetrievalMode.HYBRID
        assert result.metadata["provider_id"] == "test-provider"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_data_layer_client_handles_error() -> None:
    # Arrange
    base_url = "https://api.test"
    client = DataLayerClient(base_url=base_url)

    with patch("httpx.AsyncClient", autospec=True) as mock_client_class:
        mock_instance = mock_client_class.return_value
        mock_instance.__aenter__.return_value = mock_instance

        # Simulate a 500 error
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )
        mock_instance.get = AsyncMock(return_value=mock_response)

        # Act
        result = await client.retrieve("test")

        # Assert
        assert len(result.items) == 0
        assert "error" in result.metadata
