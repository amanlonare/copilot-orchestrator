from enum import StrEnum, auto


class IntentType(StrEnum):
    """The identified goal of the user's query.

    Attributes:
        GREETING: Conversational opening or closing.
        KNOWLEDGE: Request for factual information.
        ACTION: Request to execute a tool or task (e.g., e-commerce actions).
        CLARIFICATION: Follow-up to specify previous information.
        COMPLEX: Multi-step task requiring advanced orchestration.
        OFF_TOPIC: Query that is outside the supported business scope.
        GENERIC: Unclassified or general conversational input.
    """

    GREETING = auto()
    KNOWLEDGE = auto()
    ACTION = auto()
    CLARIFICATION = auto()
    COMPLEX = auto()
    OFF_TOPIC = auto()
    GENERIC = auto()
