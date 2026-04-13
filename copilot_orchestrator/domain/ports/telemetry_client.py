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
        """Record an operational or business event."""
        ...

    def get_callback_handler(self) -> Any:
        """Return a LangChain-compatible callback handler if supported.

        Returns:
            An instance of a BaseCallbackHandler (e.g., LangfuseCallbackHandler) or None.
        """
        ...

    def flush(self) -> None:
        """Force flush pending telemetry events."""
        ...
