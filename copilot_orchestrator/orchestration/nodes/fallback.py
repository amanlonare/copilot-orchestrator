import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.fallback_service import FallbackService
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def fallback_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to generate a fallback response when retrieval fails or is insufficient.

    Delegates to FallbackService.
    """
    logger.info("--- [Node: Fallback] Context insufficient. Generating safety response ---")

    cfg = config.get("configurable", {})
    service: FallbackService = cfg.get("fallback_service", FallbackService())

    query = state["normalized_query"]

    logger.debug(f"Fallback: Executing guardrail logic for UserID: {query.user_id}")
    answer = service.generate_fallback_response(query)
    logger.info("Fallback: Successfully generated safety answer.")
    return {"answer": answer, "fallback_flag": True}
