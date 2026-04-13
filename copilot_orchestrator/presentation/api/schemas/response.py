from typing import Any

from pydantic import BaseModel, Field


class CitationModel(BaseModel):
    """External HTTP model representing a piece of retrieved information."""

    source_id: str = Field(..., description="Unique identifier for the source document.")
    snippet: str = Field(..., description="The excerpt used from the source.")
    source_title: str | None = Field(
        default=None, description="Optional title of the source material."
    )
    score: float | None = Field(default=None, description="Relevance score.")


class ChatResponse(BaseModel):
    """External HTTP response model for the /chat endpoint."""

    answer: str = Field(..., description="The generated or selected answer for the user.")
    citations: list[CitationModel] = Field(
        default_factory=list, description="List of sources used to build the answer."
    )
    fallback_flag: bool = Field(
        default=False, description="True if the orchestrator fell back to safe/canned logic."
    )
    session_id: str | None = Field(
        default=None, description="Current or newly assigned session identifier."
    )
    trace_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata tracing the execution path."
    )
