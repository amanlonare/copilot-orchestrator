import logging
from typing import Any, cast

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def generate_answer_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to generate a grounded response using an LLM.

    Delegates to GenerationService.
    """
    logger.info("Executing generate_answer_node")

    cfg = config.get("configurable", {})
    service = cast(GenerationService, cfg.get("generation_service"))

    if not service:
        logger.error("GenerationService not found in config")
        return {"errors": [*state.get("errors", []), "Generation service missing"]}

    context = state["assembled_context"]
    query = state["normalized_query"]
    session = state["session"]

    try:
        answer = await service.generate_answer(context=context, query=query, session=session)
        return {"answer": answer}
    except Exception as e:
        logger.error("Generation failed: %s", str(e))
        return {
            "errors": [*state.get("errors", []), f"Generation failed: {e}"],
            "fallback_flag": True,
        }
