from collections.abc import Mapping
from typing import Any

from langchain_core.runnables import RunnableConfig


async def record_telemetry_event(
    config: RunnableConfig, name: str, data: Mapping[str, Any] | None = None
) -> None:
    """Helper to record an event to all configured telemetry clients.

    Args:
        config: The LangGraph RunnableConfig containing services.
        name: Name of the event.
        data: Additional metadata for the event.
    """
    configurable = config.get("configurable", {})
    clients = configurable.get("_telemetry", [])
    trace_id = configurable.get("thread_id", "unknown")

    for client in clients:
        try:
            await client.record_event(name=name, data=data, trace_id=trace_id)
        except Exception:
            # Telemetry should be non-blocking and fail-silent for the core flow
            pass
