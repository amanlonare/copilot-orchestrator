import logging
from typing import Any

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.ports.llm_provider import LLMProvider
from copilot_orchestrator.orchestration.prompts.intent_detection import (
    INTENT_DETECTION_SYSTEM_PROMPT,
)
from copilot_orchestrator.orchestration.schemas.intent_detection import IntentClassification
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def detect_intent_node(state: OrchestratorState, config: Any) -> dict[str, Any]:
    """Classifies the user's intent to determine the orchestration branch.

    This node acts as a primary router. It uses a low-latency model to identify if
    the user is looking for information (KNOWLEDGE) or wants to execute a
    predefined task (ACTION), or is just greeting.

    Args:
        state: The current LangGraph state.
        config: Configuration containing the 'llm_provider'.

    Returns:
        A dictionary updating 'detected_intent' and clearing 'tool_results'.
    """
    llm: LLMProvider = config.get("configurable", {}).get("llm_provider")
    if not llm:
        logger.error("LLMProvider not found in config. Skipping intent detection.")
        return {}

    user_query = state["normalized_query"].text

    messages = [
        AgentMessage(role=MessageRole.SYSTEM, content=INTENT_DETECTION_SYSTEM_PROMPT),
        AgentMessage(role=MessageRole.USER, content=user_query),
    ]

    try:
        # Use the newly added generate_structured port
        result: IntentClassification = await llm.generate_structured(
            messages=messages, response_model=IntentClassification
        )

        logger.info(f"Intent detected: {result.intent} | Reasoning: {result.reasoning}")

        return {
            "detected_intent": result.intent,
            "intent_metadata": {"reasoning": result.reasoning},
            "tool_results": [],  # Reset/Initialize for this turn
            "retrieved_result": None,
            "assembled_context": "",
        }
    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        from copilot_orchestrator.domain.enums.intent_type import IntentType

        return {
            "detected_intent": IntentType.KNOWLEDGE,  # Fallback
            "intent_metadata": {"reasoning": f"Fallback due to error: {e!s}"},
            "errors": [f"Intent detection failure: {e!s}"],
        }
