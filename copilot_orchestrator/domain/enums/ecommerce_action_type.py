from enum import StrEnum, auto


class EcommerceActionType(StrEnum):
    """Specific agentic actions for the e-commerce domain.

    Attributes:
        PRODUCT_SEARCH: Search for products by name, category, or features.
        PRODUCT_RECOMMEND: Get personalized product recommendations.
        ORDER_STATUS: Check the status or location of an order.
        ORDER_HISTORY: Retrieve previous orders for a user.
        ADD_TO_CART: Add a product to the shopping cart.
        VIEW_CART: View items currently in the cart.
        CHECKOUT: Start the checkout/payment process.
        INITIATE_REFUND: Start a refund request for an order.
    """

    PRODUCT_SEARCH = auto()
    PRODUCT_RECOMMEND = auto()
    ORDER_STATUS = auto()
    ORDER_HISTORY = auto()
    ADD_TO_CART = auto()
    VIEW_CART = auto()
    CHECKOUT = auto()
    INITIATE_REFUND = auto()
