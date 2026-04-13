import logging
from typing import Any, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from copilot_orchestrator.application.services.fallback_service import FallbackService
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
    if not result or service.evaluate_fallback(result.items):
        logger.info("Retrieved context insufficient. Routing to fallback.")
        return "fallback"

    return "assemble_context"


def create_orchestration_graph() -> Any:
    """Creates the compiled LangGraph for the copilot orchestrator."""
    builder = StateGraph(OrchestratorState)

    # Register Nodes
    builder.add_node("intake", intake_node)
    builder.add_node("select_strategy", select_strategy_node)
    builder.add_node("retrieve_context", retrieve_context_node)
    builder.add_node("assemble_context", assemble_context_node)
    builder.add_node("generate_answer", generate_answer_node)
    builder.add_node("finalize_response", finalize_response_node)
    builder.add_node("fallback", fallback_node)

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

    return builder


# Compile the graph
orchestrator_graph = create_orchestration_graph().compile()
