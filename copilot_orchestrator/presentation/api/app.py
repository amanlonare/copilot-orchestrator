import logging
import os
import shlex
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from copilot_orchestrator.core.config import settings
from copilot_orchestrator.core.logger import setup_logging
from copilot_orchestrator.presentation.api.dependencies import get_services
from copilot_orchestrator.presentation.api.routes import chat, health

# Initialize structured logging
setup_logging()

logger = logging.getLogger(__name__)


def _inject_mcp_into_services(services: dict[str, Any], session: ClientSession) -> None:
    """Explicitly inject MCP session into retrieval services."""
    services["_mcp_session"] = session

    if "retrieval_strategy_service" in services:
        strat_service = services["retrieval_strategy_service"]
        if hasattr(strat_service, "_gateway"):
            gateway = strat_service._gateway
            if hasattr(gateway, "client_session"):
                gateway.client_session = session
                logger.info("MCP session explicitly injected into RetrieverGateway.")
            else:
                logger.error("Gateway does not have client_session!")
        else:
            logger.error("Strat service does not have _gateway!")
    else:
        logger.error("retrieval_strategy_service not found in services!")
        logger.error(f"Available: {list(services.keys())}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Initialize shared connections
    services = get_services()

    # 1. Setup Redis Checkpointer
    if "_checkpointer" in services:
        await services["_checkpointer"].asetup()

    # 2. Setup MCP Client if enabled
    stack = AsyncExitStack()
    app.state.mcp_stack = stack

    if settings.RETRIEVER_TYPE.lower() == "mcp":
        command = settings.MCP_SERVER_COMMAND

        if not command:
            logger.warning("RETRIEVER_TYPE is 'mcp' but command not set. Falling back.")
        else:
            try:
                parts = shlex.split(command)
                server_params = StdioServerParameters(
                    command=parts[0], args=parts[1:], env=os.environ.copy()
                )

                logger.info(f"Connecting to MCP server via: {command}")
                read, write = await stack.enter_async_context(stdio_client(server_params))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                _inject_mcp_into_services(services, session)
                logger.info("MCP ClientSession initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize MCP client: {e}", exc_info=True)

    yield

    # Shutdown: Flush telemetry and close connections
    if "_telemetry" in services:
        for client in services["_telemetry"]:
            if hasattr(client, "flush"):
                client.flush()

    # Close MCP session and transport
    await stack.aclose()
    logger.info("Lifespan shutdown complete.")


app = FastAPI(
    title="Copilot Orchestrator API",
    description="Thin presentation layer for the LangGraph-based RAG orchestrator.",
    version="0.5.0",
    lifespan=lifespan,
)

# Standard CORS configuration for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with version prefix
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)


# Instrument FastAPI with OTel
if settings.OTEL_ENABLED:
    FastAPIInstrumentor.instrument_app(app)


@app.get("/")
async def root() -> dict[str, str]:
    """Root redirect or info endpoint."""
    return {"message": "Copilot Orchestrator API is running. See /docs for API documentation."}
