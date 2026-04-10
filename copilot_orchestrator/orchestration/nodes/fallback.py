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
    logger.info("Executing fallback_node")

    cfg = config.get("configurable", {})
    service: FallbackService = cfg.get("fallback_service", FallbackService())

    query = state["normalized_query"]

    answer = service.generate_fallback_response(query)
    return {"answer": answer, "fallback_flag": True}
