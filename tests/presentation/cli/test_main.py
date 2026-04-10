from unittest.mock import AsyncMock, patch

import pytest

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.presentation.cli.main import interactive_chat


@pytest.mark.asyncio
async def test_cli_one_cycle() -> None:
    """Test that the CLI performs one chat cycle and exits on 'exit'."""
    # 1. Mock Final State
    mock_final_state = {
        "session": Session(session_id="cli-session"),
        "answer": AgentMessage(role=MessageRole.ASSISTANT, content="CLI Reply"),
        "retrieved_result": None,
        "fallback_flag": False,
    }

    # 2. Mock inputs: First 'Hi', then 'exit'
    with patch("copilot_orchestrator.presentation.cli.main.Prompt.ask", side_effect=["Hi", "exit"]):
        # 3. Mock logic
        graph_path = "copilot_orchestrator.presentation.cli.main.orchestrator_graph.ainvoke"
        with patch(graph_path, new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_final_state

            # 4. Mock print to avoid terminal clutter during tests
            with patch("copilot_orchestrator.presentation.cli.main.console.print") as mock_print:
                await interactive_chat()

                # Assertions
                mock_invoke.assert_called_once()
                # Check if "CLI Reply" was printed
                # mock_print is called multiple times, we look for the reply
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any("CLI Reply" in str(c) for c in calls)
                assert any("Goodbye!" in str(c) for c in calls)
