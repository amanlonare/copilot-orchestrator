from pydantic import BaseModel, ConfigDict, Field


class EcommerceTool(BaseModel):
    """Base class for all ecommerce tools to ensure common metadata."""

    reasoning: str = Field(description="Brief explanation of why this action is being taken.")


class ProductSearch(EcommerceTool):
    """Search for products by name, category, or features."""

    model_config = ConfigDict(title="product_search")
    query: str = Field(description="The natural language search query (e.g., 'blue denim jacket').")
    category: str | None = Field(None, description="Optional category to filter results.")
    limit: int = Field(5, description="Maximum number of results to return.")


class ProductRecommend(EcommerceTool):
    """Get personalized product recommendations for the user."""

    model_config = ConfigDict(title="product_recommend")
    category: str | None = Field(None, description="Focus recommendations on a specific category.")


class OrderStatus(EcommerceTool):
    """Check the status or current location of a specific order."""

    model_config = ConfigDict(title="order_status")
    order_id: str = Field(description="The unique order ID provided by the user.")


class OrderHistory(EcommerceTool):
    """Retrieve previous orders for the authenticated user."""

    model_config = ConfigDict(title="order_history")
    limit: int = Field(10, description="Number of recent orders to fetch.")


class AddToCart(EcommerceTool):
    """Add a specific product to the user's shopping cart."""

    model_config = ConfigDict(title="add_to_cart")
    product_id: str = Field(description="The unique ID of the product to add.")
    quantity: int = Field(1, description="Number of units to add (default is 1).")


class ViewCart(EcommerceTool):
    """View items currently in the user's shopping cart."""

    model_config = ConfigDict(title="view_cart")
    pass


class Checkout(EcommerceTool):
    """Start the checkout and payment process."""

    model_config = ConfigDict(title="checkout")
    pass


class InitiateRefund(EcommerceTool):
    """Start a refund request for an existing order."""

    model_config = ConfigDict(title="initiate_refund")
    order_id: str = Field(description="The order ID for which a refund is requested.")
    reason: str = Field(description="The reason for the refund request.")


# Mapping for easy lookup
ECOMMERCE_TOOLS = [
    ProductSearch,
    ProductRecommend,
    OrderStatus,
    OrderHistory,
    AddToCart,
    ViewCart,
    Checkout,
    InitiateRefund,
]
