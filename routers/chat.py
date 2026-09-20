from uuid import uuid4
from fastapi import APIRouter, Header
from schemas.chat import ChatRequest
from services.chat_service import answer_and_persist
from database.conversation import Conversation
from database.connection import DatabaseConnection
from services.trektripster import TrekTripster

def create_router(
    database: DatabaseConnection,
    trek_tripster: TrekTripster,
) -> APIRouter:
    router = APIRouter(
        prefix="/chat",
        tags=["chat"],
    )

    @router.post("/chat-document")
    async def ask_question(
        request: ChatRequest,
        user_id: str = Header(..., alias="userid"),
    ):
        if not request.question.strip():
            return {"error": "Question cannot be empty"}

        conversation_service = Conversation(database)
        conversations = conversation_service.get_conversation(user_id=user_id)

        if conversations:
            conversation_id = conversations[0].conversation_id
        else:
            conversation_id = uuid4()
            conversation_service.create_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                title="New Convo",
            )

        return await answer_and_persist(
            user_id=user_id,
            database=database,
            trek_tripster=trek_tripster,
            conversation_id=conversation_id,
            query=request.question,
        )

    return router