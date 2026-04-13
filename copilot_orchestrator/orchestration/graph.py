import asyncio
import contextvars
import inspect
import logging
from collections.abc import Callable
from typing import Any, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from opentelemetry import trace

from copilot_orchestrator.application.services.fallback_service import FallbackService
from copilot_orchestrator.core.config import settings
from copilot_orchestrator.orchestration.nodes.assemble_context import assemble_context_node
from copilot_orchestrator.orchestration.nodes.fallback import fallback_node
from copilot_orchestrator.orchestration.nodes.finalize_response import finalize_response_node
from copilot_orchestrator.orchestration.nodes.generate_answer import generate_answer_node
from copilot_orchestrator.orchestration.nodes.intake import intake_node
from copilot_orchestrator.orchestration.nodes.retrieve_context import retrieve_context_node
from copilot_orchestrator.orchestration.nodes.select_strategy import select_strategy_node
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


def route_after_retrieval(
    state: OrchestratorState, config: RunnableConfig
) -> Literal["assemble_context", "fallback"]:
    """Conditional edge to decide if we should proceed to generation or fallback."""
    cfg = config.get("configurable", {})
    service: FallbackService = cfg.get("fallback_service", FallbackService())

    result = state.get("retrieved_result")
    if not result or service.evaluate_fallback(
        result.items, min_score=settings.RAG_RELEVANCE_THRESHOLD
    ):
        logger.info("Retrieved context insufficient. Routing to fallback.")
        return "fallback"

    return "assemble_context"


def traced_node(name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wraps a LangGraph node to accurately record an OpenTelemetry span.
    Handles context propagation to sync functions dispatched to thread pools."""
    tracer = trace.get_tracer(__name__)
    is_async = asyncio.iscoroutinefunction(fn)
    takes_config = "config" in inspect.signature(fn).parameters

    async def wrapper(state: OrchestratorState, config: RunnableConfig | None = None) -> Any:
        logger.info(f"==> [Node Execution] Entering: {name}")

        if is_async:
            with tracer.start_as_current_span(f"node.{name}") as span:
                span.set_attribute("node.name", name)
                result = await fn(state, config) if takes_config else await fn(state)
        else:
            ctx = contextvars.copy_context()

            def run() -> Any:
                with tracer.start_as_current_span(f"node.{name}") as span:
                    span.set_attribute("node.name", name)
                    return fn(state, config) if takes_config else fn(state)

            result = await asyncio.get_event_loop().run_in_executor(None, ctx.run, run)

        keys = list(result.keys()) if isinstance(result, dict) else type(result)
        logger.info(f"<== [Node Execution] Exiting: {name} | Output keys: {keys}")
        return result

    return wrapper


def create_orchestration_graph(checkpointer: BaseCheckpointSaver[Any] | None = None) -> Any:
    """Creates and compiles the LangGraph for the copilot orchestrator.

    Args:
        checkpointer: Optional persistence checkpointer (e.g., Redis).
    """
    builder = StateGraph(OrchestratorState)

    # Register Nodes with OTel span wrappers
    builder.add_node("intake", traced_node("intake", intake_node))
    builder.add_node("select_strategy", traced_node("select_strategy", select_strategy_node))
    builder.add_node("retrieve_context", traced_node("retrieve_context", retrieve_context_node))
    builder.add_node("assemble_context", traced_node("assemble_context", assemble_context_node))
    builder.add_node("generate_answer", traced_node("generate_answer", generate_answer_node))
    builder.add_node("finalize_response", traced_node("finalize_response", finalize_response_node))
    builder.add_node("fallback", traced_node("fallback", fallback_node))

    # Define Edges
    builder.add_edge(START, "intake")
    builder.add_edge("intake", "select_strategy")
    builder.add_edge("select_strategy", "retrieve_context")

    # Conditional Edge after Retrieval
    builder.add_conditional_edges(
        "retrieve_context",
        route_after_retrieval,
        {"assemble_context": "assemble_context", "fallback": "fallback"},
    )

    builder.add_edge("assemble_context", "generate_answer")
    builder.add_edge("generate_answer", "finalize_response")
    builder.add_edge("fallback", "finalize_response")
    builder.add_edge("finalize_response", END)

    return builder.compile(checkpointer=checkpointer)


# Default unpersisted graph for testing or basic CLI usage
orchestrator_graph = create_orchestration_graph()
