from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from routers import chat
from schemas.chat import ChatRequest


@pytest.mark.asyncio
async def test_empty_question_returns_error(monkeypatch):
    conversation_service = Mock()

    monkeypatch.setattr(
        chat,
        "Conversation",
        Mock(return_value=conversation_service),
    )

    router = chat.create_router(Mock(), Mock())
    endpoint = router.routes[0].endpoint

    result = await endpoint(
        ChatRequest(question="   "),
        "user-1",
    )

    assert result == {"error": "Question cannot be empty"}
    conversation_service.get_conversation.assert_not_called()


@pytest.mark.asyncio
async def test_existing_conversation_is_reused(monkeypatch):
    conversation_id = UUID("22222222-2222-2222-2222-222222222222")
    conversation_service = Mock()
    conversation_service.get_conversation.return_value = [
        SimpleNamespace(conversation_id=conversation_id)
    ]

    answer_mock = AsyncMock(return_value="answer")

    monkeypatch.setattr(
        chat,
        "Conversation",
        Mock(return_value=conversation_service),
    )
    monkeypatch.setattr(chat, "answer_and_persist", answer_mock)

    router = chat.create_router(Mock(), Mock())
    endpoint = router.routes[0].endpoint

    result = await endpoint(
        ChatRequest(question="What should I visit?"),
        "user-1",
    )

    assert result == "answer"
    conversation_service.create_conversation.assert_not_called()
    answer_mock.assert_awaited_once()
    assert answer_mock.await_args.kwargs["conversation_id"] == conversation_id


@pytest.mark.asyncio
async def test_new_conversation_is_created_when_none_exists(monkeypatch):
    conversation_service = Mock()
    conversation_service.get_conversation.return_value = []

    answer_mock = AsyncMock(return_value="answer")

    monkeypatch.setattr(
        chat,
        "Conversation",
        Mock(return_value=conversation_service),
    )
    monkeypatch.setattr(chat, "answer_and_persist", answer_mock)

    router = chat.create_router(Mock(), Mock())
    endpoint = router.routes[0].endpoint

    result = await endpoint(
        ChatRequest(question="Plan my trip"),
        "user-1",
    )

    assert result == "answer"
    conversation_service.create_conversation.assert_called_once()

    create_args = conversation_service.create_conversation.call_args.kwargs
    assert create_args["user_id"] == "user-1"
    assert create_args["title"] == "New Convo"
    assert create_args["conversation_id"] is not None