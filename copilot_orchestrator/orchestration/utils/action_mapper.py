import logging
from typing import Any

logger = logging.getLogger(__name__)


class ActionMapper:
    """Utility to map internal LangGraph tool results to frontend-safe SSE actions.

    This follows clean architecture by decoupling the internal state of the
    orchestrator from the public API contract sent to the widget.
    """

    @staticmethod
    def map_tool_call_to_action(tool_call: dict[str, Any]) -> dict[str, Any] | None:
        """Map a raw LLM tool call to a frontend action intent.

        This can be used to notify the frontend that an action is STARTING.
        """
        name = tool_call.get("name")
        args = tool_call.get("args", {})

        if name == "product_search":
            return {
                "type": "product_search",
                "status": "pending",
                "payload": {"query": args.get("query")},
            }
        elif name == "add_to_cart":
            return {
                "type": "add_to_cart",
                "status": "pending",
                "payload": {"variant_id": args.get("variant_id")},
            }
        return None

    @staticmethod
    def map_tool_result_to_action(tool_name: str, result: Any) -> dict[str, Any] | None:
        """Map a completed tool execution result to a frontend action.

        Args:
            tool_name: The name of the tool that was executed.
            result: The raw output from the tool execution.

        Returns:
            A dictionary containing the action type, status, and payload.
        """
        # We only care about specific commerce actions for the widget UI
        if tool_name == "product_search":
            return {
                "type": "product_search",
                "status": "success",
                "payload": {"results": result if isinstance(result, list) else []},
            }

        elif tool_name == "add_to_cart":
            # result is typically a success/error message or object from the mock client
            return {"type": "add_to_cart", "status": "success", "payload": {"result": result}}

        return None
