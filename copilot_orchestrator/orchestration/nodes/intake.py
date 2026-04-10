import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.application.services.query_intake_service import QueryIntakeService
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def intake_node(state: OrchestratorState, config: RunnableConfig) -> dict[str, Any]:
    """Node to process raw input into a structured UserQuery.

    Delegates to QueryIntakeService.
    """
    logger.info("Executing intake_node")

    # In a prod-ready system, we'd pull the service from a registry or provider
    # For now, we instantiate or use from config if provided
    service = config.get("configurable", {}).get("query_intake_service", QueryIntakeService())

    request = state["request"]

    try:
        query = service.process(
            raw_query=request.query.text,
            session_id=request.query.session_id,
            user_id=request.query.user_id,
            metadata=request.query.metadata,
        )
        return {"normalized_query": query}
    except Exception as e:
        logger.error("Intake failed: %s", str(e))
        return {"errors": [*state.get("errors", []), f"Intake failed: {e}"], "fallback_flag": True}
