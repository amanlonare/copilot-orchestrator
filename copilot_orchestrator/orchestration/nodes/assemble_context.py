import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.context_builder_service import ContextBuilderService
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def assemble_context_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to format retrieved citations into a context string.

    Delegates to ContextBuilderService.
    """
    logger.info("Executing assemble_context_node")

    cfg = config.get("configurable", {})
    service: ContextBuilderService = cfg.get("context_builder_service", ContextBuilderService())

    result = state.get("retrieved_result")
    if not result or not result.items:
        logger.info("No retrieved items to assemble.")
        return {"assembled_context": "", "fallback_flag": True}

    context = service.build_context(result.items)
    return {"assembled_context": context}
