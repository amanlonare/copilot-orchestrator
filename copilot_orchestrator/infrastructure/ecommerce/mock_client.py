import logging
from typing import Any

logger = logging.getLogger(__name__)


class MockEcommerceClient:
    """Mock implementation of an e-commerce backend for local development and testing.

    Provides simulated endpoints for product discovery, order tracking, and
    cart management without requiring an external API.
    """

    async def search_products(self, query: str) -> list[dict[str, Any]]:
        """Simulates searching for products in a catalog.

        Args:
            query: The search term (e.g., 'jacket').

        Returns:
            A list of product dictionaries matching the query.
        """
        logger.info(f"[MOCK] Searching products for: {query}")
        # Static mock results
        items: list[dict[str, Any]] = [
            {"id": "p_001", "name": "Classic Denim Jacket", "price": 89.99, "stock": 15},
            {"id": "p_002", "name": "Slim-fit Chinos", "price": 54.50, "stock": 22},
            {"id": "p_003", "name": "Basic White T-Shirt", "price": 19.99, "stock": 50},
        ]
        return [it for it in items if query.lower() in str(it["name"]).lower()] or [items[0]]

    async def get_order_status(self, order_id: str) -> dict[str, Any]:
        """Simulates looking up status for a specific order.

        Args:
            order_id: The unique identifier for the order (e.g., 'AB123').

        Returns:
            A dictionary containing delivery status and estimated dates.
        """
        logger.info(f"[MOCK] Fetching status for order: {order_id}")
        return {
            "order_id": order_id,
            "status": "SHIPPED",
            "estimated_delivery": "2026-04-20",
            "items": ["p_001"],
        }

    async def add_to_cart(self, product_id: str, quantity: int) -> dict[str, Any]:
        """Simulates adding a product to the user's shopping basket.

        Args:
            product_id: Target product ID.
            quantity: Number of items to add.

        Returns:
            A status dictionary indicating success and the new total.
        """
        logger.info(f"[MOCK] Adding {quantity} of {product_id} to cart.")
        return {
            "success": True,
            "message": f"Successfully added {quantity} of {product_id} to your basket.",
            "cart_total": 89.99 * quantity,
        }

    async def initiate_refund(self, order_id: str, reason: str) -> dict[str, Any]:
        """Simulates initiating a refund for an order.

        Args:
            order_id: Target order ID.
            reason: Reason for refund request.

        Returns:
            A status dictionary indicating the refund request was received.
        """
        logger.info(f"[MOCK] Initiating refund for order {order_id}. Reason: {reason}")
        return {
            "success": True,
            "order_id": order_id,
            "status": "REFUND_INITIATED",
            "message": "Your refund request has been received and is being processed.",
        }
