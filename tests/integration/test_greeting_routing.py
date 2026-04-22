from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.runnables import RunnableConfig

from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.enums.intent_type import IntentType
from copilot_orchestrator.orchestration.nodes.detect_intent import detect_intent_node
from copilot_orchestrator.orchestration.nodes.generate_greeting import (
    generate_greeting_node,
)
from copilot_orchestrator.orchestration.schemas.intent_detection import (
    IntentClassification,
)
from copilot_orchestrator.orchestration.state import OrchestratorState


@pytest.mark.asyncio
async def test_greeting_pipeline() -> None:
    """Verifies that a greeting query is correctly routed and results in an answer."""
    # Setup
    mock_llm = AsyncMock()

    # 1. Intent Detection return
    mock_llm.generate_structured.return_value = IntentClassification(
        intent=IntentType.GREETING, reasoning="User is saying hello"
    )

    # 2. Greeting Generation return
    mock_llm.generate.return_value = MagicMock(content="Hello! How can I help you today?")

    state = cast(
        OrchestratorState,
        {
            "normalized_query": UserQuery(text="Hello there!"),
            "session": MagicMock(history=[]),
        },
    )
    # Mock GenerationService
    mock_gen_service = AsyncMock()
    mock_gen_service.generate_greeting.return_value = MagicMock(
        content="Hello! How can I help you today?"
    )

    config = cast(
        RunnableConfig,
        {"configurable": {"llm_provider": mock_llm, "generation_service": mock_gen_service}},
    )

    # Pipeline Execution
    # Node 1: Detect Intent
    res1 = await detect_intent_node(state, config)
    state.update(cast(OrchestratorState, res1))
    assert state["detected_intent"] == IntentType.GREETING

    # Node 2: Generate Greeting (In the graph, this is routed based on IntentType.GREETING)
    res2 = await generate_greeting_node(state, config)
    state.update(cast(OrchestratorState, res2))

    assert state["answer"] is not None
    assert "Hello" in state["answer"].content
