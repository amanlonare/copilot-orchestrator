from abc import ABC, abstractmethod
from typing import Any


class EcommerceProvider(ABC):
    """Abstract Base Class for all E-commerce platform providers.

    This ensures a consistent interface whether we are talking to Shopify,
    BigCommerce, or a Mock client.
    """

    @abstractmethod
    async def search_products(self, query: str) -> list[dict[str, Any]]:
        """Search for products in the catalog."""
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str) -> dict[str, Any]:
        """Fetch the status of a specific order."""
        pass

    @abstractmethod
    async def add_to_cart(self, variant_id: str, quantity: int) -> dict[str, Any]:
        """Add a specific variant to the shopping cart."""
        pass

    @abstractmethod
    async def initiate_refund(self, order_id: str, reason: str) -> dict[str, Any]:
        """Initiate a refund for an order."""
        pass
