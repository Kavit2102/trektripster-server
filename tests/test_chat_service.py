from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID
import pytest
from services.chat_service import answer_and_persist

@pytest.mark.asyncio
async def test_answer_and_persist_creates_and_updates_message():
    message = SimpleNamespace(
        message_id=UUID("11111111-1111-1111-1111-111111111111")
    )
    message_service = Mock()
    trek_tripster = Mock()

    with (
        patch("services.chat_service.Message", return_value=message_service),
        patch(
            "services.chat_service.asyncio.to_thread",
            new_callable=AsyncMock,
        ) as to_thread,
    ):
        to_thread.side_effect = [message, "Generated answer", None]

        result = await answer_and_persist(
            user_id="user-1",
            database=Mock(),
            trek_tripster=trek_tripster,
            conversation_id="conversation-1",
            query="What should I visit?",
        )

    assert result == "Generated answer"

    message_service.create_message.assert_called_once_with(
        user_id="user-1",
        conversation_id="conversation-1",
        query="What should I visit?",
        content="",
    )

    message_service.update_message.assert_called_once_with(
        message_id=message.message_id,
        content="Generated answer",
    )

    trek_tripster.assert_not_called()