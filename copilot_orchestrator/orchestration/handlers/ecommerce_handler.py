import logging
from typing import Any

from copilot_orchestrator.domain.entities.action import Action
from copilot_orchestrator.domain.enums.ecommerce_action_type import EcommerceActionType
from copilot_orchestrator.infrastructure.ecommerce.mock_client import MockEcommerceClient

logger = logging.getLogger(__name__)


class EcommerceActionHandler:
    """Handler for all E-commerce domain actions.

    Delegates to MockEcommerceClient to simulate real tool execution.
    """

    def __init__(self) -> None:
        # In a production system, this client would be injected
        self._client: MockEcommerceClient = MockEcommerceClient()

    async def execute(self, action: Action) -> list[dict[str, Any]]:
        """Map EcommerceActionType to specific tool methods.

        Args:
            action: The action entity containing the type (must match EcommerceActionType).

        Returns:
            List of execution results.
        """
        results: list[dict[str, Any]] = []
        action_type = action.type
        params = action.parameters or {}

        try:
            if action_type == EcommerceActionType.PRODUCT_SEARCH:
                query = params.get("query", "")
                products = await self._client.search_products(query)
                results.append({"tool": "product_search", "output": products})

            elif action_type == EcommerceActionType.ORDER_STATUS:
                order_id = params.get("order_id", "unknown")
                status = await self._client.get_order_status(order_id)
                results.append({"tool": "order_status", "output": status})

            elif action_type == EcommerceActionType.ADD_TO_CART:
                pid = params.get("product_id", "")
                qty = params.get("quantity", 1)
                cart_res = await self._client.add_to_cart(pid, qty)
                results.append({"tool": "add_to_cart", "output": cart_res})

            elif action_type == EcommerceActionType.VIEW_CART:
                # Mock cart view
                results.append({"tool": "view_cart", "output": {"items": [], "total": 0.0}})

            elif action_type == EcommerceActionType.INITIATE_REFUND:
                order_id = params.get("order_id", "unknown")
                reason = params.get("reason", "No reason provided")
                refund_res = await self._client.initiate_refund(order_id, reason)
                results.append({"tool": "initiate_refund", "output": refund_res})

            else:
                logger.warning(f"Ecommerce action type '{action_type}' not implemented.")
                results.append(
                    {
                        "tool": str(action_type),
                        "output": "Tool execution not implemented for this e-commerce action.",
                    }
                )

        except Exception as e:
            logger.error(f"Ecommerce tool execution failed: {e}")
            raise

        return results
