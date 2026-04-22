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
    actions = state.get("resolved_actions", [])
    if not actions:
        logger.warning("No actions resolved. Skipping tool execution.")
        return {}

    # Inject handler via config if available, otherwise fallback to static registry
    cfg = config.get("configurable", {})
    all_results = []
    all_errors = []

    for action in actions:
        domain = action.domain
        if domain is None:
            logger.error("Action domain is None. Cannot determine handler.")
            all_results.append({"tool": action.type, "output": "Missing action domain"})
            all_errors.append(f"Action domain missing for {action.type}")
            continue

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
                all_results.append(
                    {"tool": action.type, "output": f"No execution handler for domain {domain}"}
                )
                all_errors.append(f"Missing handler for {domain}")
                continue

        try:
            logger.info(f"Executing action '{action.type}' via {handler.__class__.__name__}")
            results = await handler.execute(action)
            all_results.extend(results)
            logger.info(
                f"Tool execution '{action.type}' complete. Received {len(results)} result(s)."
            )
        except Exception as e:
            logger.error(f"Tool execution failed for domain {domain}: {e}")
            all_results.append({"tool": action.type, "output": str(e)})
            all_errors.append(f"Execution error [action={action.type}]: {e!s}")

    return {
        "tool_results": all_results,
        "errors": (
            [*state.get("errors", []), *all_errors] if all_errors else state.get("errors", [])
        ),
    }
