from enum import StrEnum, auto


class ActionDomain(StrEnum):
    """Business domains for specialized agentic actions.

    Attributes:
        ECOMMERCE: Actions related to product search, ordering, and cart management.
        FINANCIAL: Actions related to payments, accounts, and transactions.
        SUPPORT: Actions related to customer service and ticketing.
    """

    ECOMMERCE = auto()
    FINANCIAL = auto()
    SUPPORT = auto()
