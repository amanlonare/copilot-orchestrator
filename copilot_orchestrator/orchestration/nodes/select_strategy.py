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
    logger.info("--- [Node: Select Strategy] Determining best retrieval approach ---")

    service = config.get("configurable", {}).get("retrieval_strategy_service")

    if not service:
        logger.warning(
            "SelectStrategy: RetrievalStrategyService not found in config. Defaulting to HYBRID."
        )
        return {"retrieval_strategy": RetrievalMode.HYBRID}

    strategy = service.select_strategy(state["normalized_query"])
    logger.info(f"SelectStrategy: Decided on strategy: {strategy}")
    return {"retrieval_strategy": strategy}
