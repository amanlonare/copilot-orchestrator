from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TelemetryClient(Protocol):
    """Contract for recording telemetry patterns, latency, and operational events.

    Implementations (e.g., Structured Logger, Langfuse, OpenTelemetry)
    must provide non-blocking or efficient event recording.
    """

    async def record_event(
        self,
        name: str,
        data: Mapping[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> None:
        """Record an operational or business event.

        Args:
            name: Human-readable identifier for the event (e.g., "generation_started").
            data: Structured payload for the event.
            trace_id: Optional correlation ID for distributed tracing.
        """
        ...
