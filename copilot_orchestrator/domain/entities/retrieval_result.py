from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.enums.intent_type import IntentType
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode


@dataclass(slots=True)
class IntentResult:
    """The result of an intent classification step.

    Attributes:
        intent: The identified category of the user's goal.
        confidence: Probability the classification is correct.
        reason: Justification or thinking trace for the intent.
    """

    intent: IntentType
    confidence: float | None = None
    reason: str | None = None


@dataclass(slots=True)
class ContextBundle:
    """A bundle of retrieved context for the orchestrator.

    Attributes:
        query: The internal query used for retrieval.
        citations: Detailed source references.
        assembled_text: Compressed or formatted context text for the prompt.
        metadata: Extra data from the retrieval engine.
    """

    query: str
    citations: list[Citation] = field(default_factory=list)
    assembled_text: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalResult:
    """The outcome of a retrieval operation from a gateway.

    Attributes:
        items: List of citations (chunks) found.
        mode: The search method used (SEMANTIC, etc.).
        latency_ms: Performance metric for the retrieval call.
        metadata: Provider-specific debug or tracing data.
    """

    items: list[Citation] = field(default_factory=list)
    mode: RetrievalMode = RetrievalMode.SEMANTIC
    latency_ms: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)
