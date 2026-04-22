import json
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from copilot_orchestrator.domain.entities.query import UserQuery
from copilot_orchestrator.domain.enums.intent_type import IntentType
from copilot_orchestrator.orchestration.nodes.detect_intent import (
    detect_intent_node,
)
from copilot_orchestrator.orchestration.nodes.execute_tools import execute_tools_node
from copilot_orchestrator.orchestration.nodes.format_action_response import (
    format_action_response_node,
)
from copilot_orchestrator.orchestration.nodes.resolve_action import resolve_action_node
from copilot_orchestrator.orchestration.schemas.intent_detection import IntentClassification
from copilot_orchestrator.orchestration.state import OrchestratorState


@pytest.mark.asyncio
async def test_order_status_pipeline() -> None:
    """Verifies end-to-end routing for an order status request."""
    # Setup
    mock_llm = AsyncMock()

    # 1. Intent Detection return (Node 1)
    mock_llm.generate_structured.return_value = IntentClassification(
        intent=IntentType.ACTION, reasoning="Order tracking"
    )

    # 2. Action Resolution return (Node 2) - Native Tool Call
    mock_llm.generate.side_effect = [
        # First call: Tool call for order_status
        MagicMock(
            content="",
            tool_calls=[
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "order_status",
                        "arguments": json.dumps({"order_id": "ABC-999"}),
                    },
                }
            ],
        ),
        # Second call: Format response content (Node 4)
        MagicMock(content="Your order ABC-999 is SHIPPED."),
    ]

    state = cast(
        OrchestratorState,
        {
            "normalized_query": UserQuery(text="Where is my order ABC-999?"),
        },
    )
    config = {"configurable": {"llm_provider": mock_llm}}

    # Pipeline Execution
    # Node 1: Detect Intent
    res1 = await detect_intent_node(state, config)
    state.update(cast(OrchestratorState, res1))
    assert state["detected_intent"] == IntentType.ACTION

    # Node 2: Resolve Action
    res2 = await resolve_action_node(state, config)
    state.update(cast(OrchestratorState, res2))
    # The Action entity now uses the literal tool name (snake_case)
    assert len(state["resolved_actions"]) == 1
    assert state["resolved_actions"][0].type == "order_status"
    assert state["resolved_actions"][0].parameters["order_id"] == "ABC-999"

    # Node 3: Execute Tools
    res3 = await execute_tools_node(state, config)
    state.update(cast(OrchestratorState, res3))
    assert len(state["tool_results"]) == 1
    assert state["tool_results"][0]["tool"] == "order_status"
    assert state["tool_results"][0]["output"]["status"] == "SHIPPED"

    # Node 4: Format Response
    res4 = await format_action_response_node(state, config)
    state.update(cast(OrchestratorState, res4))
    assert state["answer"] is not None
    assert "Your order ABC-999 is SHIPPED" in state["answer"].content
