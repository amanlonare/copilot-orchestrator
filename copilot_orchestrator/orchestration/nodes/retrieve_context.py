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
    query_text = state["normalized_query"].text[:40]
    logger.info(f"--- [Node: Retrieve] Fetching context for: '{query_text}...' ---")

    cfg = config.get("configurable", {})
    service = cast(RetrievalStrategyService, cfg.get("retrieval_strategy_service"))

    if not service:
        logger.error("RetrieveContext: RetrievalStrategyService missing from config!")
        return {"errors": [*state.get("errors", []), "Retrieval service missing"]}

    query = state["normalized_query"]
    mode = state.get("retrieval_strategy")

    try:
        logger.debug(f"RetrieveContext: Executing retrieval (Mode: {mode})")
        result = await service.retrieve_for_query(query=query, mode=mode)

        num_results = len(result.items) if result else 0
        logger.info(f"RetrieveContext: Retrieval complete. Found {num_results} context items.")
        return {"retrieved_result": result}
    except Exception as e:
        logger.error("Retrieval execution failed: %s", str(e))
        return {
            "errors": [*state.get("errors", []), f"Retrieval failed: {e}"],
            "fallback_flag": True,
        }
