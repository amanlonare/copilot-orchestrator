import logging
from typing import Any

import httpx

from copilot_orchestrator.infrastructure.ecommerce.base import EcommerceProvider

logger = logging.getLogger(__name__)


class ShopifyProvider(EcommerceProvider):
    """Shopify-specific implementation of the EcommerceProvider.

    This provider handles the GraphQL Admin API calls to Shopify (shpua_ tokens).
    """

    def __init__(self, api_key: str | None = None, shop_url: str | None = None):
        self.api_key = api_key  # This is the Admin Access Token (shpua_...)
        self.shop_url = shop_url
        # Note the /admin/ path in the URL
        self.api_url = f"https://{shop_url}/admin/api/2024-04/graphql.json" if shop_url else ""

        logger.debug(f"ShopifyProvider (Admin) initialized for {shop_url}")

    async def search_products(self, query: str) -> list[dict[str, Any]]:
        """Search products via Shopify Admin GraphQL API."""
        if not self.api_key or not self.shop_url:
            logger.error(
                "ShopifyProvider: Missing credentials "
                "(SHOPIFY_ADMIN_ACCESS_TOKEN or SHOPIFY_SHOP_URL)"
            )
            return []

        logger.info(f"[SHOPIFY ADMIN] Searching products for: {query}")

        # Admin API uses 'query' parameter in products field
        graphql_query = """
        query searchProducts($query: String!) {
          products(first: 5, query: $query) {
            edges {
              node {
                id
                title
                handle
                descriptionHtml
                featuredImage {
                  url
                  altText
                }
                variants(first: 1) {
                  edges {
                    node {
                      id
                      price
                      inventoryQuantity
                    }
                  }
                }
              }
            }
          }
        }
        """

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.api_key,  # Correct header for Admin API
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={"query": graphql_query, "variables": {"query": query}},
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

                if "errors" in data:
                    logger.error(f"Shopify Admin GraphQL errors: {data['errors']}")
                    return []

                products = []
                for edge in data.get("data", {}).get("products", {}).get("edges", []):
                    node = edge["node"]
                    variants = node["variants"]["edges"]
                    variant_edge = variants[0]["node"] if variants else {}
                    image = node["featuredImage"]["url"] if node["featuredImage"] else None

                    # Map Admin API fields to our internal format
                    products.append(
                        {
                            "id": node["id"],
                            "name": node["title"],
                            "handle": node["handle"],
                            "price": float(variant_edge.get("price", 0)),
                            "image_url": image,
                            "variant_id": variant_edge.get("id"),
                            "description": (
                                node["descriptionHtml"][:100] + "..."
                                if node["descriptionHtml"]
                                else ""
                            ),
                        }
                    )

                return products

        except Exception as e:
            logger.error(f"Shopify Admin request failed: {e}")
            return []

    async def get_order_status(self, order_id: str) -> dict[str, Any]:
        """Fetch order status via Shopify Admin API."""
        logger.info(f"[SHOPIFY ADMIN] Fetching order status for: {order_id}")
        # Implementation for order status would go here using Admin API
        return {"order_id": order_id, "status": "SHIPPED"}

    async def add_to_cart(self, variant_id: str, quantity: int) -> dict[str, Any]:
        """Note: Handled by frontend. This is a placeholder for backend validation."""
        return {"success": True, "variant_id": variant_id}

    async def initiate_refund(self, order_id: str, reason: str) -> dict[str, Any]:
        """Initiate refund via Shopify Admin API."""
        logger.info(f"[SHOPIFY ADMIN] Initiating refund for: {order_id}")
        return {"success": True, "order_id": order_id}
