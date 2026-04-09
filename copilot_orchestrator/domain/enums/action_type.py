from enum import StrEnum, auto


class ActionType(StrEnum):
    """Category of tool invocation or system action.

    Attributes:
        SEARCH: Retrieval of external knowledge or documents.
        EMAIL: Communication with external users or systems.
        RESERVATION: Booking or scheduling operation.
        CALCULATION: Mathematical or data processing task.
        INTERNAL: System-level state change or logging.
    """

    SEARCH = auto()
    EMAIL = auto()
    RESERVATION = auto()
    CALCULATION = auto()
    INTERNAL = auto()
