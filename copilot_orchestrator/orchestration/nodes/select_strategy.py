import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def select_strategy_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to determine the retrieval strategy.

    Delegates to RetrievalStrategyService.
    """
    logger.info("Executing select_strategy_node")

    # RetrievalStrategyService requires a gateway, but here we only need 'select_strategy'
    # which is currently pure. In a real system, we'd pull from config/registry.
    service = config.get("configurable", {}).get("retrieval_strategy_service")

    # Fallback to a default if not provided (for MVP/testing)
    if not service:
        # We shouldn't really reach here if the graph is set up correctly
        return {"retrieval_strategy": RetrievalMode.HYBRID}

    strategy = service.select_strategy(state["normalized_query"])
    return {"retrieval_strategy": strategy}
