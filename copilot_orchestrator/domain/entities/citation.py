from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Citation:
    """A reference to a source chunk used in generation.

    Attributes:
        source_id: Unique identifier for the source document.
        snippet: The specific text fragment retrieved.
        source_title: Human-readable name of the source.
        score: Relevance score from the retriever.
        url: Direct link to the source material.
        metadata: Extra structured data (e.g., page number, author).
    """

    source_id: str
    snippet: str
    source_title: str | None = None
    score: float | None = None
    url: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
