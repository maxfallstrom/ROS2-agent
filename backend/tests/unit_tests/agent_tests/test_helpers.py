import pytest
from unittest.mock import AsyncMock, patch, Mock
from agent.helpers.classify_prompt import classify_prompt, PromptClassification
from langchain_openai import ChatOpenAI

@pytest.mark.asyncio
async def test_classify_prompt_returns_incomplete_with_follow_up():
    state = {
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }

    with patch.object(ChatOpenAI, "ainvoke", new_callable=AsyncMock) as mock_llm, \
         patch("agent.helpers.classify_prompt.get_parser") as mock_get_parser:

        mock_llm.return_value = {
            "role": "assistant",
            "content": '{"status": "incomplete", "question": "What should the robot do?"}'
        }

        fake_parser = Mock()
        fake_parser.invoke.return_value = PromptClassification(
            status="incomplete",
            question="What should the robot do?"
        )
        mock_get_parser.return_value = fake_parser

        result = await classify_prompt(state)

        assert isinstance(result, PromptClassification)
        assert result.status == "incomplete"
        assert result.question == "What should the robot do?"



@pytest.mark.asyncio
async def test_classify_prompt_returns_complete_if_many_messages():
    state = {
        "messages": [
            {"role": "user", "content": "I need a robot"},
            {"role": "assistant", "content": "What do you need it to do?"},
            {"role": "user", "content": "To pick up boxes in a warehouse"},
            {"role": "assistant", "content": "Noted."},
            {"role": "user", "content": "It should handle 10kg"}
        ]
    }

    result = await classify_prompt(state)
    assert result.status == "complete"

