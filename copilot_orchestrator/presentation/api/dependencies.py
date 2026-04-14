import logging
from collections.abc import AsyncGenerator
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from openai import AsyncOpenAI
from redis.asyncio import Redis

from copilot_orchestrator.application.services.context_builder_service import ContextBuilderService
from copilot_orchestrator.application.services.fallback_service import FallbackService
from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.application.services.query_intake_service import QueryIntakeService
from copilot_orchestrator.application.services.retrieval_strategy_service import (
    RetrievalStrategyService,
)
from copilot_orchestrator.application.services.session_service import SessionService
from copilot_orchestrator.core.config import settings
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway
from copilot_orchestrator.domain.ports.telemetry_client import TelemetryClient
from copilot_orchestrator.infrastructure.llm.openai_client import OpenAIClient
from copilot_orchestrator.infrastructure.retrieval.mcp_retriever import MCPRetrieverGateway
from copilot_orchestrator.infrastructure.retrieval.mock_retriever import (
    MockRetrieverGateway,
)
from copilot_orchestrator.infrastructure.sessions.redis_repository import (
    RedisSessionRepository,
)
from copilot_orchestrator.infrastructure.telemetry.langfuse_adapter import LangfuseAdapter
from copilot_orchestrator.infrastructure.telemetry.otel_adapter import OTelAdapter
from copilot_orchestrator.orchestration.graph import (
    create_orchestration_graph,
)

logger = logging.getLogger(__name__)

# Global services container for the MVP
_services: dict[str, Any] = {}


def get_services() -> dict[str, Any]:
    """Provide the application services needed by the orchestrator graph.
    Instantiates infrastructure lazily if empty.
    """
    if not _services:
        # 1. Initialize Adapters
        openai_key = (
            settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else "dummy"
        )
        openai_async_client = AsyncOpenAI(api_key=openai_key)
        llm_provider = OpenAIClient(async_client=openai_async_client, model=settings.OPENAI_MODEL)

        # Configure the Retriever Gateway based on settings
        retriever_type = settings.RETRIEVER_TYPE.lower()
        retriever_gateway: RetrieverGateway
        if retriever_type == "mcp":
            retriever_gateway = MCPRetrieverGateway(services=_services)
        else:
            retriever_gateway = MockRetrieverGateway()

        # 2. Redis & Persistence
        redis_url = settings.REDIS_URL
        redis_client = Redis.from_url(redis_url, decode_responses=True)
        session_store = RedisSessionRepository(redis_client=redis_client)

        # LangGraph Checkpointer
        checkpointer: BaseCheckpointSaver[Any] = AsyncRedisSaver(redis_client=redis_client)

        # 3. Telemetry Adapters
        telemetry_clients: list[TelemetryClient] = []

        # Langfuse
        if (
            settings.LANGFUSE_ENABLED
            and settings.LANGFUSE_PUBLIC_KEY
            and settings.LANGFUSE_SECRET_KEY
        ):
            telemetry_clients.append(
                LangfuseAdapter(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
            )

        # OTel / Honeycomb
        if settings.OTEL_ENABLED and settings.HONEYCOMB_API_KEY:
            # Honeycomb OTLP configuration
            _telemetry_client = OTelAdapter(
                service_name=settings.OTEL_SERVICE_NAME,
                api_key=settings.HONEYCOMB_API_KEY,
                environment=settings.ENVIRONMENT,
                dataset=settings.HONEYCOMB_DATASET,
            )
            logger.info("Initialized OpenTelemetry (Honeycomb) client.")
            telemetry_clients.append(_telemetry_client)

        # 4. Initialize Services (Mutate global dict to preserve references)
        _services.update(
            {
                "llm_provider": llm_provider,
                "query_intake_service": QueryIntakeService(),
                "retrieval_strategy_service": RetrievalStrategyService(retriever_gateway),
                "context_builder_service": ContextBuilderService(),
                "generation_service": GenerationService(llm_provider),
                "session_service": SessionService(session_store),
                "fallback_service": FallbackService(),
                "_telemetry": telemetry_clients,
                "_redis": redis_client,
                "_checkpointer": checkpointer,
                "_graph": create_orchestration_graph(checkpointer=checkpointer),
            }
        )

    return _services


async def get_orchestrator_graph() -> AsyncGenerator[Any, None]:
    """FastAPI dependency that yields the compiled LangGraph execution graph."""
    services = get_services()
    yield services["_graph"]
