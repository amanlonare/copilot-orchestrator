from copilot_orchestrator.core.config import settings
from copilot_orchestrator.infrastructure.ecommerce.base import EcommerceProvider
from copilot_orchestrator.infrastructure.ecommerce.mock_client import MockEcommerceClient
from copilot_orchestrator.infrastructure.ecommerce.providers.shopify_provider import ShopifyProvider


class EcommerceProviderFactory:
    """Factory to instantiate the correct e-commerce provider."""

    @staticmethod
    def get_provider() -> EcommerceProvider:
        """Pick a provider based on central settings."""
        provider_type = settings.ECOMMERCE_PROVIDER.lower()

        if provider_type == "shopify":
            api_key = (
                settings.SHOPIFY_ADMIN_ACCESS_TOKEN.get_secret_value()
                if settings.SHOPIFY_ADMIN_ACCESS_TOKEN
                else None
            )
            return ShopifyProvider(api_key=api_key, shop_url=settings.SHOPIFY_SHOP_URL)

        # Default to Mock
        return MockEcommerceClient()
