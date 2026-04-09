from enum import StrEnum, auto


class RetrievalMode(StrEnum):
    """Modes of context retrieval from knowledge sources.

    Attributes:
        SEMANTIC: Vector-based similarity search.
        KEYWORD: BM-25 or exact string search.
        HYBRID: Combined ranking of semantic and keyword results.
    """

    SEMANTIC = auto()
    KEYWORD = auto()
    HYBRID = auto()
