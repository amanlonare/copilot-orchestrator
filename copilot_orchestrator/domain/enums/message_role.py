from enum import StrEnum, auto


class MessageRole(StrEnum):
    """Roles in a conversation interaction.

    Attributes:
        SYSTEM: Administrative instructions for the LLM.
        USER: Raw input from the end user.
        ASSISTANT: Generated output from the LLM.
        TOOL: Execution results from an external utility or agent.
    """

    SYSTEM = auto()
    USER = auto()
    ASSISTANT = auto()
    TOOL = auto()
