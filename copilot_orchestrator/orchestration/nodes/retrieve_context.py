import logging
from typing import Any, cast

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.retrieval_strategy_service import (
    RetrievalStrategyService,
)
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def retrieve_context_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to retrieve context from knowledge bases.

    Delegates to RetrievalStrategyService.
    """
    logger.info("Executing retrieve_context_node")

    cfg = config.get("configurable", {})
    service = cast(RetrievalStrategyService, cfg.get("retrieval_strategy_service"))

    if not service:
        logger.error("RetrievalStrategyService not found in config")
        return {"errors": [*state.get("errors", []), "Retrieval service missing"]}

    query = state["normalized_query"]
    mode = state.get("retrieval_strategy")

    try:
        result = await service.retrieve_for_query(query=query, mode=mode)
        return {"retrieved_result": result}
    except Exception as e:
        logger.error("Retrieval execution failed: %s", str(e))
        return {
            "errors": [*state.get("errors", []), f"Retrieval failed: {e}"],
            "fallback_flag": True,
        }
