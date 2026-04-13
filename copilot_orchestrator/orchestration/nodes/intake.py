import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.query_intake_service import QueryIntakeService
from copilot_orchestrator.orchestration.state import OrchestratorState
from copilot_orchestrator.orchestration.telemetry_utils import record_telemetry_event

logger = logging.getLogger(__name__)


async def intake_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to process raw input into a structured UserQuery.

    Delegates to QueryIntakeService.
    """
    logger.info(
        f"--- [Node: Intake] Starting processing for UserID: {state['request'].query.user_id} ---"
    )
    await record_telemetry_event(config, "node_started", {"node": "intake"})

    # Trace incoming data
    raw_text = state["request"].query.text
    logger.debug(f"Intake: Processing raw query: '{raw_text[:50]}...'")

    service = config.get("configurable", {}).get("query_intake_service", QueryIntakeService())

    try:
        query = service.process(
            raw_query=raw_text,
            session_id=state["request"].query.session_id,
            user_id=state["request"].query.user_id,
            metadata=state["request"].query.metadata,
        )
        logger.info(f"Intake: Successfully normalized query. Length: {len(raw_text)} chars.")
        await record_telemetry_event(config, "node_completed", {"node": "intake"})
        return {"normalized_query": query}
    except Exception as e:
        logger.error("Intake failed: %s", str(e))
        return {"errors": [*state.get("errors", []), f"Intake failed: {e}"], "fallback_flag": True}
