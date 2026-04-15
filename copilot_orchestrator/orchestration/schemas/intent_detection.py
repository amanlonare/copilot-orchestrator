from pydantic import BaseModel, ConfigDict, Field

from copilot_orchestrator.domain.enums.intent_type import IntentType


class IntentClassification(BaseModel):
    """Pydantic schema for structured intent classification.

    Attributes:
        intent: The categorized intent of the user message (e.g., KNOWLEDGE, ACTION).
        reasoning: A brief explanation for the chosen classification to aid debugging.
    """

    model_config = ConfigDict(extra="forbid")

    intent: IntentType = Field(description="The categorized intent of the user message.")
    reasoning: str = Field(description="Brief explanation for the chosen classification.")
