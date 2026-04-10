from collections.abc import Mapping
from typing import Any, TypedDict

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.query import OrchestratorRequest, UserQuery
from copilot_orchestrator.domain.entities.retrieval_result import RetrievalResult
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.retrieval_mode import RetrievalMode


class OrchestratorState(TypedDict):
    """Canonical orchestration state for the LangGraph runtime.

    This state acts as a thin coordination layer between application services.
    Avoid SDK-specific objects or raw provider responses here.
    """

    # Input
    request: OrchestratorRequest

    # Processed Query
    normalized_query: UserQuery

    # Context & Session
    session: Session
    retrieval_strategy: RetrievalMode

    # Retrieval Outcomes
    retrieved_result: RetrievalResult
    assembled_context: str

    # Generation
    answer: AgentMessage | None

    # Metadata & Flags
    fallback_flag: bool
    trace_metadata: Mapping[str, Any]
    errors: list[str]
    warnings: list[str]
