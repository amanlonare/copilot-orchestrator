from unittest.mock import MagicMock

import pytest

from copilot_orchestrator.infrastructure.telemetry.structured_logger import StructuredLoggerClient


@pytest.mark.asyncio
async def test_structured_logger_records_event(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    mock_logger = MagicMock()
    # We monkeypatch the loguru logger to verify calls
    monkeypatch.setattr(
        "copilot_orchestrator.infrastructure.telemetry.structured_logger.logger", mock_logger
    )

    # We need to mock the bind result as well because StructuredLoggerClient calls bind()
    mock_bound_logger = MagicMock()
    mock_logger.bind.return_value = mock_bound_logger

    client = StructuredLoggerClient(service_name="test-service")

    # Act
    await client.record_event("test_event", data={"key": "value"}, trace_id="t123")

    # Assert
    mock_logger.bind.assert_called_with(service="test-service")
    mock_bound_logger.info.assert_called_once()

    # Extract payload
    args, _ = mock_bound_logger.info.call_args
    payload = args[0]
    assert payload["event"] == "test_event"
    assert payload["data"]["key"] == "value"
    assert payload["trace_id"] == "t123"
