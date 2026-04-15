from typing import cast
from unittest.mock import AsyncMock

import pytest

from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.enums.intent_type import IntentType
from copilot_orchestrator.orchestration.nodes.detect_intent import (
    detect_intent_node,
)
from copilot_orchestrator.orchestration.schemas.intent_detection import IntentClassification
from copilot_orchestrator.orchestration.state import OrchestratorState


@pytest.mark.asyncio
async def test_detect_intent_knowledge() -> None:
    # Setup
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = IntentClassification(
        intent=IntentType.KNOWLEDGE, reasoning="User is asking about policies."
    )

    state = cast(
        OrchestratorState,
        {
            "normalized_query": UserQuery(text="What is your return policy?"),
        },
    )
    config = {"configurable": {"llm_provider": mock_llm}}

    # Execute
    result = await detect_intent_node(state, config)

    # Verify
    assert result["detected_intent"] == IntentType.KNOWLEDGE
    mock_llm.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_detect_intent_action() -> None:
    # Setup
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = IntentClassification(
        intent=IntentType.ACTION, reasoning="User wants to track an order."
    )

    state = cast(
        OrchestratorState,
        {
            "normalized_query": UserQuery(text="Where is my order 123?"),
        },
    )
    config = {"configurable": {"llm_provider": mock_llm}}

    # Execute
    result = await detect_intent_node(state, config)

    # Verify
    assert result["detected_intent"] == IntentType.ACTION


@pytest.mark.asyncio
async def test_detect_intent_fallback() -> None:
    # Setup
    mock_llm = AsyncMock()
    mock_llm.generate_structured.side_effect = Exception("LLM Down")

    state = cast(
        OrchestratorState,
        {
            "normalized_query": UserQuery(text="Help me"),
        },
    )
    config = {"configurable": {"llm_provider": mock_llm}}

    # Execute
    result = await detect_intent_node(state, config)

    # Verify
    assert result["detected_intent"] == IntentType.KNOWLEDGE  # Fallback
    assert "errors" in result
