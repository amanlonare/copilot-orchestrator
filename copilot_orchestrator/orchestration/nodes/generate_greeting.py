import logging
from typing import Any, cast

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def generate_greeting_node(
    state: OrchestratorState, config: RunnableConfig
) -> dict[str, Any]:
    """Node to generate a friendly greeting.

    Delegates to GenerationService.
    """
    logger.info("--- [Node: Generate Greeting] Generating friendly greeting ---")

    cfg = config.get("configurable", {})
    service = cast(GenerationService, cfg.get("generation_service"))

    if not service:
        logger.error("GenerateGreeting: GenerationService missing from config!")
        return {"errors": [*state.get("errors", []), "Generation service missing"]}

    query = state["normalized_query"]
    session = state["session"]

    try:
        answer = await service.generate_greeting(query=query, session=session)
        return {"answer": answer}
    except Exception as e:
        logger.error("Greeting generation failed: %s", str(e))
        return {
            "errors": [*state.get("errors", []), f"Greeting generation failed: {e}"],
        }
