from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """External HTTP request model for the /chat endpoint."""

    query: str = Field(..., description="The user's input string.")
    user_id: str | None = Field(
        default=None, description="Optional unique identifier for the user."
    )
    session_id: str | None = Field(
        default=None, description="Optional identifier for the conversation session."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extra structured data (e.g., origin, device).",
    )
