from enum import StrEnum, auto


class IntentType(StrEnum):
    """The identified goal of the user's query.

    Attributes:
        GREETING: Conversational opening or closing.
        KNOWLEDGE: Request for factual information.
        TRANSACTIONAL: Request for action or state change.
        CLARIFICATION: Follow-up to specify previous information.
        COMPLEX: Multi-step task requiring advanced orchestration.
        GENERIC: Unclassified or general conversational input.
    """

    GREETING = auto()
    KNOWLEDGE = auto()
    TRANSACTIONAL = auto()
    CLARIFICATION = auto()
    COMPLEX = auto()
    GENERIC = auto()
