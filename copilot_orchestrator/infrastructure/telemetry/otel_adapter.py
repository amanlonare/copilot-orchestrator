from collections.abc import Mapping
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from copilot_orchestrator.domain.ports.telemetry_client import TelemetryClient


class OTelAdapter(TelemetryClient):
    """Adapter for OpenTelemetry (Honeycomb) tracing."""

    def __init__(
        self,
        service_name: str,
        api_key: str,
        environment: str = "development",
        dataset: str | None = None,
        endpoint: str = "https://api.honeycomb.io",
    ):
        """Initialize OTel tracer with Honeycomb settings.

        Args:
            service_name: Name of the service for OTel resource.
            api_key: Honeycomb API key (x-honeycomb-team).
            endpoint: OTLP HTTP endpoint for Honeycomb.
        """
        resource = Resource.create(
            {
                "service.name": service_name,
                "deployment.environment.name": environment,
            }
        )
        provider = TracerProvider(resource=resource)

        # Configure OTLP Exporter with Honeycomb headers
        headers = {
            "x-honeycomb-team": api_key,
            "x-honeycomb-dataset": dataset or service_name,
        }
        exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", headers=headers)

        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        # Set the global tracer provider
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

    async def record_event(
        self,
        name: str,
        data: Mapping[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> None:
        """Record an event as a span.

        Note: In OTel, discrete events are often logged as spans or span events.
        For the MVP, this is a no-op to satisfy the Protocol.
        """
        pass

    def get_callback_handler(self) -> Any:
        """OTel manages context via spans rather than a LangChain callback in this adapter."""
        return None

    def flush(self) -> None:
        """Force flush pending OTel spans."""
        # Tracer provider isn't directly flushable, but processor is.
        # For this MVP, we rely on the BatchSpanProcessor's shutdown.
        pass
