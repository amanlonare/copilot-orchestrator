import os
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI

from copilot_orchestrator.application.services.context_builder_service import ContextBuilderService
from copilot_orchestrator.application.services.fallback_service import FallbackService
from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.application.services.query_intake_service import QueryIntakeService
from copilot_orchestrator.application.services.retrieval_strategy_service import (
    RetrievalStrategyService,
)
from copilot_orchestrator.application.services.session_service import SessionService
from copilot_orchestrator.domain.ports.retriever_gateway import RetrieverGateway
from copilot_orchestrator.infrastructure.llm.openai_client import OpenAIClient
from copilot_orchestrator.infrastructure.retrieval.mcp_retriever import MCPRetrieverGateway
from copilot_orchestrator.infrastructure.retrieval.mock_retriever import (
    MockRetrieverGateway,
)
from copilot_orchestrator.infrastructure.sessions.in_memory_session_store import (
    InMemorySessionStore,
)
from copilot_orchestrator.orchestration.graph import orchestrator_graph

# Global services container for the MVP
_services: dict[str, Any] = {}


def get_services() -> dict[str, Any]:
    """Provide the application services needed by the orchestrator graph.
    Instantiates infrastructure lazily if empty.
    """
    global _services  # noqa: PLW0603
    if not _services:
        # 1. Initialize Adapters
        # Use OpenAI if key is present, otherwise we'd normally use a mock,
        # but for this MVP, we expect OPENAI_API_KEY to be available or it will fail on generation.
        openai_async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
        llm_provider = OpenAIClient(async_client=openai_async_client, model="gpt-4o")
        # Configure the Retriever Gateway based on environment variable
        retriever_type = os.getenv("RETRIEVER_TYPE", "mock").lower()
        retriever_gateway: RetrieverGateway
        if retriever_type == "mcp":
            # For this Phase, we instantiate the MCP gateway.
            # In Phase 7 (Deployment), we will set up the actual SSE/Stdio
            # async context manager in FastAPI's lifespan to pass a live ClientSession.
            retriever_gateway = MCPRetrieverGateway(mcp_client_session=None)
        else:
            retriever_gateway = MockRetrieverGateway()

        session_store = InMemorySessionStore()

        # 2. Initialize Services
        _services = {
            "query_intake_service": QueryIntakeService(),
            "retrieval_strategy_service": RetrievalStrategyService(retriever_gateway),
            "context_builder_service": ContextBuilderService(),
            "generation_service": GenerationService(llm_provider),
            "session_service": SessionService(session_store),
            "fallback_service": FallbackService(),
        }

    return _services


async def get_orchestrator_graph() -> AsyncGenerator[Any, None]:
    """FastAPI dependency that yields the compiled LangGraph execution graph."""
    # orchestrator_graph is globally instantiated in graph.py
    yield orchestrator_graph
