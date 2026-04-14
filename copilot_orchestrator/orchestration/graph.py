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
from copilot_orchestrator.domain.enums.intent_type import IntentType
from copilot_orchestrator.orchestration.nodes.assemble_context import assemble_context_node
from copilot_orchestrator.orchestration.nodes.detect_intent import detect_intent_node
from copilot_orchestrator.orchestration.nodes.execute_tools import execute_tools_node
from copilot_orchestrator.orchestration.nodes.fallback import fallback_node
from copilot_orchestrator.orchestration.nodes.finalize_response import finalize_response_node
from copilot_orchestrator.orchestration.nodes.format_action_response import (
    format_action_response_node,
)
from copilot_orchestrator.orchestration.nodes.generate_answer import generate_answer_node
from copilot_orchestrator.orchestration.nodes.intake import intake_node
from copilot_orchestrator.orchestration.nodes.resolve_action import resolve_action_node
from copilot_orchestrator.orchestration.nodes.retrieve_context import retrieve_context_node
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


def route_after_intent(
    state: OrchestratorState, config: RunnableConfig
) -> Literal["retrieve_context", "finalize_response", "resolve_action"]:
    """Conditional edge to fork the orchestration flow based on detected intent.

    Routing logic:
    - ACTION: Routes to tool-resolution branch (e-commerce actions).
    - GREETING: Routes directly to finalization if no search is needed.
    - KNOWLEDGE: Routes to standard RAG pipeline (Retrieval -> Generation).

    Args:
        state: The current orchestrator state.
        config: Runnable configuration.

    Returns:
        The identifier of the next node to execute.
    """
    intent = state.get("detected_intent")

    if intent == IntentType.ACTION:
        logger.info("Action intent detected. Routing to resolve_action branch.")
        return "resolve_action"

    if intent == IntentType.GREETING:
        logger.info("Greeting detected. Routing directly to finalize_response.")
        return "finalize_response"

    # Default to KNOWLEDGE path
    return "retrieve_context"


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

        # Enhanced result logging using rich for pretty repr and loguru for colored tags
        from loguru import logger as loguru_logger
        from rich.pretty import pretty_repr

        # Exclude massive objects from the 'Result' view to keep logs readable
        display_result = result
        if isinstance(result, dict):
            display_result = {
                k: v
                for k, v in result.items()
                if k not in ["assembled_context", "retrieved_result"]
            }

        formatted_result = pretty_repr(display_result, max_string=300)

        # Log with colors enabled via opt(colors=True)
        loguru_logger.opt(colors=True).info(
            f"<blue><b>[Node Result: {name}]</b></blue>\n{formatted_result}"
        )

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
    builder.add_node("detect_intent", traced_node("detect_intent", detect_intent_node))
    builder.add_node("resolve_action", traced_node("resolve_action", resolve_action_node))
    builder.add_node("execute_tools", traced_node("execute_tools", execute_tools_node))
    builder.add_node(
        "format_action_response", traced_node("format_action_response", format_action_response_node)
    )
    builder.add_node("retrieve_context", traced_node("retrieve_context", retrieve_context_node))
    builder.add_node("assemble_context", traced_node("assemble_context", assemble_context_node))
    builder.add_node("generate_answer", traced_node("generate_answer", generate_answer_node))
    builder.add_node("finalize_response", traced_node("finalize_response", finalize_response_node))
    builder.add_node("fallback", traced_node("fallback", fallback_node))

    # Define Edges
    builder.add_edge(START, "intake")
    builder.add_edge("intake", "detect_intent")

    # Intent Branching
    builder.add_conditional_edges(
        "detect_intent",
        route_after_intent,
        {
            "retrieve_context": "retrieve_context",
            "finalize_response": "finalize_response",
            "resolve_action": "resolve_action",
        },
    )

    # Action Path
    builder.add_edge("resolve_action", "execute_tools")
    builder.add_edge("execute_tools", "format_action_response")
    builder.add_edge("format_action_response", "finalize_response")

    # Knowledge path
    # (Previously select_strategy -> retrieve_context, now directly to retrieve_context)

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


if __name__ == "__main__":
    # Generate graph visualization
    # This requires an internet connection (for mermaid.ink) or local mermaid/pygraphviz install
    try:
        print("Generating graph visualization...")
        png_data = orchestrator_graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_data)
        print("Graph visualization matches the current flow and was saved to graph.png")
    except Exception as e:
        print(f"Failed to generate graph visualization: {e}")
        print("Note: This often requires 'pygraphviz' or an internet connection.")
