import json
import logging
from typing import Any, cast

from copilot_orchestrator.core.config import settings
from copilot_orchestrator.domain.entities.action import Action
from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.enums.action_domain import ActionDomain
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.domain.ports.llm_provider import LLMProvider
from copilot_orchestrator.orchestration.prompts.action_resolution import (
    get_action_resolution_prompt,
)
from copilot_orchestrator.orchestration.schemas.action_tools import ECOMMERCE_TOOLS
from copilot_orchestrator.orchestration.state import OrchestratorState

logger = logging.getLogger(__name__)


async def resolve_action_node(state: OrchestratorState, config: Any) -> dict[str, Any]:
    """Resolves specific action parameters based on the active business domain.

    This Tier 2 node uses the configured ACTIVE_DOMAIN to determine which
    specialized tools and parameters to extract from the user's natural language.

    Args:
        state: The current LangGraph state containing the 'normalized_query'.
        config: Configuration containing the 'llm_provider'.

    Returns:
        A dictionary containing the 'resolved_action' domain entity.
    """
    llm: LLMProvider = config.get("configurable", {}).get("llm_provider")
    if not llm:
        logger.error("LLMProvider not found in config. Skipping action resolution.")
        return {}

    user_query = state["normalized_query"].text
    active_domain = settings.ACTIVE_DOMAIN.lower()

    # Determine which action type enum and prompt to use
    if active_domain == ActionDomain.ECOMMERCE.value:
        system_prompt = get_action_resolution_prompt(active_domain)
        domain_enum = ActionDomain.ECOMMERCE
    else:
        # Fallback to general resolution
        logger.warning(f"Unsupported domain: {active_domain}. Falling back to general resolution.")
        system_prompt = get_action_resolution_prompt("generic")
        domain_enum = None

    messages = [
        AgentMessage(role=MessageRole.SYSTEM, content=system_prompt),
        AgentMessage(role=MessageRole.USER, content=user_query),
    ]

    try:
        # Use native tool calling
        response = await llm.generate(
            messages=messages,
            tools=(
                cast(Any, ECOMMERCE_TOOLS)
                if active_domain == ActionDomain.ECOMMERCE.value
                else None
            ),
        )

        if not response.tool_calls:
            # If the model returned content but no tools, log it for debugging
            if response.content:
                logger.info(f"Model returned text instead of tool: {response.content}")

            logger.warning(f"No tool calls generated for query: {user_query}")
            return {
                "errors": [
                    "No actionable intent found in resolution phase. "
                    "Please be more specific about the product or order."
                ]
            }

        # For now, we take the first tool call (single action resolution)
        tool_call = response.tool_calls[0]
        # Handle both dict and object (Sequence[Mapping] vs list[ToolCall])
        fn = tool_call.get("function", {})
        tool_name = fn.get("name", "unknown")

        raw_arguments = fn.get("arguments", "{}")
        arguments = json.loads(raw_arguments)

        # Build the Action entity
        resolved_action = Action(
            type=tool_name,
            label=f"Execute {tool_name} in {active_domain}",
            domain=domain_enum,
            parameters=arguments,
            metadata={
                "reasoning": arguments.get("reasoning", "No reasoning provided."),
                "tier": "tier_2_resolution",
                "active_domain": active_domain,
                "tool_call_id": tool_call.get("id"),
            },
            confidence=1.0,
        )

        logger.info(f"Action resolved [{active_domain}]: {tool_name}")

        return {"resolved_action": resolved_action, "action_metadata": resolved_action.metadata}
    except Exception as e:
        logger.error(f"Action resolution failed for domain {active_domain}: {e}")
        return {"errors": [f"Action resolution error ({active_domain}): {e!s}"]}
