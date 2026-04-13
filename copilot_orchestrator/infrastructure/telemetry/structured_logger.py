from collections.abc import Mapping
from typing import Any

from loguru import logger

from copilot_orchestrator.domain.ports.telemetry_client import TelemetryClient


class StructuredLoggerClient(TelemetryClient):
    """Infrastructure adapter for emitting structured telemetry via loguru.

    This client implements the TelemetryClient port, producing consistent
    JSON-formatted logs for observability and performance tracking.
    """

    def __init__(self, service_name: str = "copilot-orchestrator"):
        """Initialize the logger client.

        Args:
            service_name: Name of the originating service for log context.
        """
        self._logger = logger.bind(service=service_name)

    async def record_event(
        self,
        name: str,
        data: Mapping[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> None:
        """Log a structured event.

        Args:
            name: The event identifier.
            data: Payload containing metrics or metadata.
            trace_id: Correlation ID for the current request flow.
        """
        event_payload = {
            "event": name,
            "data": data or {},
        }
        if trace_id:
            event_payload["trace_id"] = trace_id

        # We log at INFO level for operational events.
        # loguru's default configuration will handle the formatting.
        self._logger.info(event_payload)

    def get_callback_handler(self) -> Any:
        """Structured logger does not support LangChain callbacks directly."""
        return None

    def flush(self) -> None:
        """No-op for loguru as it flushes automatically or via sinks."""
        pass
