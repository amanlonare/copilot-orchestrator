from enum import StrEnum, auto


class ActionType(StrEnum):
    """Category of tool invocation or system action.

    Attributes:
        SEARCH: Retrieval of external knowledge or documents.
        EMAIL: Communication with external users or systems.
        INTERNAL: System-level state change or logging.
    """

    SEARCH = auto()
    EMAIL = auto()
    INTERNAL = auto()
    ORDER_STATUS = auto()
    KNOWLEDGE = auto()
