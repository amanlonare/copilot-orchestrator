import logging
from typing import Any

from copilot_orchestrator.domain.enums.action_domain import ActionDomain
from copilot_orchestrator.orchestration.handlers.ecommerce_handler import EcommerceActionHandler
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def execute_tools_node(state: OrchestratorState, config: Any) -> dict[str, Any]:
    """Dispatches the resolved action to the appropriate domain handler.

    This node takes the 'resolved_action' from the state and delegates
    execution to a specialized handler based on the action's domain.

    Args:
        state: The current LangGraph state containing 'resolved_action'.
        config: Configuration containing provider info.

    Returns:
        A dictionary containing 'tool_results' with raw tool outputs.
    """
    action = state.get("resolved_action")
    if not action:
        logger.warning("No action resolved. Skipping tool execution.")
        return {}

    domain = action.domain
    if domain is None:
        logger.error("Action domain is None. Cannot determine handler.")
        return {
            "tool_results": [{"tool": "error", "output": "Missing action domain"}],
            "errors": ["Action domain is None"],
        }

    # Inject handler via config if available, otherwise fallback to static registry
    cfg = config.get("configurable", {})

    # Check if a specific handler was injected for this domain
    # Expected key format: '{domain}_handler'
    handler_key = f"{domain.value.lower()}_handler"
    handler = cfg.get(handler_key)

    if not handler:
        logger.debug(
            f"Handler '{handler_key}' not found in config. "
            "Falling back to default handler initialization."
        )
        if domain == ActionDomain.ECOMMERCE:
            handler = EcommerceActionHandler()
        else:
            logger.error(f"No handler registered for domain: {domain}")
            return {
                "tool_results": [
                    {"tool": "error", "output": f"No execution handler for domain {domain}"}
                ],
                "errors": [f"Missing handler for {domain}"],
            }

    try:
        logger.info(f"Executing action '{action.type}' via {handler.__class__.__name__}")
        results = await handler.execute(action)
        logger.info(f"Tool execution complete. Received {len(results)} result(s).")
        return {"tool_results": results}

    except Exception as e:
        logger.error(f"Tool execution failed for domain {domain}: {e}")
        return {
            "tool_results": [{"tool": "error", "output": str(e)}],
            "errors": [f"Execution error: {e!s}"],
        }
