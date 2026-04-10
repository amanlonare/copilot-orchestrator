from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import AsyncOpenAI

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.enums.message_role import MessageRole
from copilot_orchestrator.infrastructure.llm.openai_client import OpenAIClient


@pytest.mark.asyncio  # type: ignore[misc]
async def test_openai_client_generate_calls_sdk_correctly() -> None:
    # Arrange
    mock_sdk = MagicMock(spec=AsyncOpenAI)
    mock_sdk.chat = MagicMock()
    mock_sdk.chat.completions = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello from AI"))]
    mock_response.usage = MagicMock()
    mock_response.usage.model_dump.return_value = {"total_tokens": 10}

    mock_sdk.chat.completions.create = AsyncMock(return_value=mock_response)

    client = OpenAIClient(async_client=mock_sdk, model="test-model")
    messages = [AgentMessage(role=MessageRole.USER, content="Hello")]

    # Act
    result = await client.generate(messages)

    # Assert
    assert result.content == "Hello from AI"
    assert result.role == MessageRole.ASSISTANT
    mock_sdk.chat.completions.create.assert_called_once()

    _, kwargs = mock_sdk.chat.completions.create.call_args
    assert kwargs["model"] == "test-model"
    # Verify mapping
    sent_messages = kwargs["messages"]
    assert len(sent_messages) == 1
    assert sent_messages[0]["role"] == "user"
    assert sent_messages[0]["content"] == "Hello"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_openai_client_handles_empty_content() -> None:
    mock_sdk = MagicMock(spec=AsyncOpenAI)
    mock_sdk.chat = MagicMock()
    mock_sdk.chat.completions = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None))]
    mock_response.usage = None

    mock_sdk.chat.completions.create = AsyncMock(return_value=mock_response)

    client = OpenAIClient(async_client=mock_sdk)
    result = await client.generate([AgentMessage(role=MessageRole.USER, content="Hi")])

    assert result.content == ""
    assert result.role == MessageRole.ASSISTANT


@pytest.mark.asyncio  # type: ignore[misc]
async def test_openai_client_includes_name_in_payload() -> None:
    mock_sdk = MagicMock(spec=AsyncOpenAI)
    mock_sdk.chat = MagicMock()
    mock_sdk.chat.completions = MagicMock()
    mock_sdk.chat.completions.create = AsyncMock()

    client = OpenAIClient(async_client=mock_sdk)
    messages = [AgentMessage(role=MessageRole.SYSTEM, content="You are a bot", name="system_bot")]

    await client.generate(messages)

    _, kwargs = mock_sdk.chat.completions.create.call_args
    assert kwargs["messages"][0]["name"] == "system_bot"
