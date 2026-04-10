import logging
from typing import Any, cast

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.session_service import SessionService
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def finalize_response_node(
    state: OrchestratorState, config: RunnableConfig
) -> dict[str, Any]:
    """Node to persist the final answer and session state.

    Delegates to SessionService.
    """
    logger.info("Executing finalize_response_node")

    cfg = config.get("configurable", {})
    service = cast(SessionService, cfg.get("session_service"))

    if not service:
        logger.error("SessionService not found in config")
        return {"errors": [*state.get("errors", []), "Session service missing"]}

    session = state["session"]
    answer = state.get("answer")

    if not answer:
        logger.warning("No answer found in state during finalization.")
        return {}

    try:
        await service.append_and_save(session=session, message=answer)
        return {"session": session}
    except Exception as e:
        logger.error("Session finalization failed: %s", str(e))
        return {"errors": [*state.get("errors", []), f"Finalization failed: {e}"]}
