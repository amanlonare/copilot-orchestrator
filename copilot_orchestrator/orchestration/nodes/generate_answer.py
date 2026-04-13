import logging
from typing import Any, cast

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.orchestration.state import OrchestratorState
from copilot_orchestrator.orchestration.telemetry_utils import record_telemetry_event

logger = logging.getLogger(__name__)


async def generate_answer_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to generate a grounded response using an LLM.

    Delegates to GenerationService.
    """
    logger.info("--- [Node: Generate Answer] Calling LLM for final response ---")
    await record_telemetry_event(config, "node_started", {"node": "generate_answer"})

    cfg = config.get("configurable", {})
    service = cast(GenerationService, cfg.get("generation_service"))

    if not service:
        logger.error("GenerateAnswer: GenerationService missing from config!")
        return {"errors": [*state.get("errors", []), "Generation service missing"]}

    context = state["assembled_context"]
    query = state["normalized_query"]
    session = state["session"]

    try:
        has_context = "YES" if context else "NO"
        logger.debug(f"GenerateAnswer: Generating grounded answer (Context present: {has_context})")

        answer = await service.generate_answer(context=context, query=query, session=session)

        usage = answer.metadata.get("usage", {})
        tokens = usage.get("total_tokens", "N/A")
        logger.info(f"GenerateAnswer: Success. Tokens: {tokens}")

        await record_telemetry_event(
            config,
            "node_completed",
            {
                "node": "generate_answer",
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                },
            },
        )
        return {"answer": answer}
    except Exception as e:
        logger.error("Generation failed: %s", str(e))
        return {
            "errors": [*state.get("errors", []), f"Generation failed: {e}"],
            "fallback_flag": True,
        }
