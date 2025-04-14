import pytest
from unittest.mock import AsyncMock, patch
from agent.helpers.classify_prompt import classify_prompt, PromptClassification

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


@pytest.mark.asyncio
async def test_classify_prompt_returns_incomplete_with_follow_up():
    state = {
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }

    with patch("agent.helpers.classify_prompt.prompt.ainvoke", new_callable=AsyncMock) as mock_prompt, \
         patch("agent.helpers.classify_prompt.llm.ainvoke", new_callable=AsyncMock) as mock_llm, \
         patch("agent.helpers.classify_prompt.parser.invoke") as mock_parser:

        mock_prompt.return_value = {"role": "system", "content": "Prompt generated"}
        mock_llm.return_value = {"role": "assistant", "content": '{"status": "incomplete", "question": "What should the robot do?"}'}
        mock_parser.return_value = PromptClassification(status="incomplete", question="What should the robot do?")

        result = await classify_prompt(state)

        assert result.status == "incomplete"
        assert result.question == "What should the robot do?"
