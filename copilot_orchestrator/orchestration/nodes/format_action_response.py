import logging
from typing import Any

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.ports.llm_provider import LLMProvider
from copilot_orchestrator.orchestration.prompts.response_formatting import (
    FORMAT_RESPONSE_SYSTEM_PROMPT,
)
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def format_action_response_node(state: OrchestratorState, config: Any) -> dict[str, Any]:
    """Formats the final conversational answer based on executed tool outputs.

    This node grounds the LLM response in the specific data returned by
    infrastructure tools (e.g., product lists, order details) to ensure
    accuracy and professionalism.

    Args:
        state: The current LangGraph state containing 'tool_results' and 'normalized_query'.
        config: Configuration containing the 'llm_provider'.

    Returns:
        A dictionary updating the 'answer' field with a grounded AgentMessage.
    """
    llm: LLMProvider = config.get("configurable", {}).get("llm_provider")
    results = state.get("tool_results", [])
    user_query = state["normalized_query"].text

    # Prepare context from results
    results_context = "\n".join([f"Tool {r['tool']} returned: {r['output']}" for r in results])

    messages = [
        AgentMessage(role=MessageRole.SYSTEM, content=FORMAT_RESPONSE_SYSTEM_PROMPT),
        AgentMessage(
            role=MessageRole.USER,
            content=f"User Query: {user_query}\n\nTool Results:\n{results_context}",
        ),
    ]

    try:
        response = await llm.generate(messages)
        return {"answer": response}
    except Exception as e:
        logger.error(f"Response formatting failed: {e}")
        return {
            "answer": AgentMessage(
                role=MessageRole.ASSISTANT,
                content=(
                    "I processed your request but encountered an error formatting the final answer."
                ),
            )
        }
