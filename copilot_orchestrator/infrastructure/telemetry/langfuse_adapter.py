import os
from collections.abc import Mapping
from typing import Any

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from copilot_orchestrator.domain.ports.telemetry_client import TelemetryClient


class LangfuseAdapter(TelemetryClient):
    """Adapter for Langfuse telemetry."""

    def __init__(self, public_key: str, secret_key: str, host: str):
        """Initialize Langfuse client globally.

        Args:
            public_key: Langfuse public key.
            secret_key: Langfuse secret key.
            host: Langfuse host URL.
        """
        # Sync env vars so CallbackHandler's background worker can read them
        os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
        os.environ["LANGFUSE_SECRET_KEY"] = secret_key
        os.environ["LANGFUSE_HOST"] = host

        self._public_key = public_key
        self.langfuse = Langfuse(public_key=public_key, secret_key=secret_key, base_url=host)

    async def record_event(
        self,
        name: str,
        data: Mapping[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> None:
        """Record an event in Langfuse."""
        # In v3, events must be created on a trace object, not the top-level client.
        # Automatic tracing via CallbackHandler handles this. This method is a no-op.
        pass

    def get_callback_handler(self) -> Any:
        """Get the official LangChain callback handler for Langfuse.
        In v3+, it automatically picks up the global client configuration.
        """
        return CallbackHandler(public_key=self._public_key)

    def flush(self) -> None:
        """Force flush pending events to Langfuse."""
        self.langfuse.flush()
