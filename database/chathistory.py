from typing import Sequence
from uuid import UUID
from sqlmodel import Session, select
from database.models import Message
from database.connection import DatabaseConnection

class ChatHistoryService:
    """
    Handles chat message persistence and retrieval.
    """

    def __init__(self, database: DatabaseConnection) -> None:
        self.database = database

    def save_message(
        self,
        user_id: str,
        conversation_id: UUID,
        # role: str,
        query: str,
        content: str,
    ) -> Message:

        messages = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            # role=role,
            query=query,
            content=content,
        )

        print(f"Saving message: {messages}")

        with Session(self.database.get_engine()) as session:
            try:
                session.add(messages)
                session.commit()
                session.refresh(messages)

            except Exception as e:
                session.rollback()
                print(f"Error saving message: {e}")
                raise

        print("Saved Message!!")

        return messages

    def get_history(
        self,
        user_id: str,
        conversation_id: UUID,
        limit: int = 50,
    ) -> Sequence[Message]:

        statement = (
            select(Message)
            .where(
                Message.user_id == user_id,
                Message.conversation_id == conversation_id,
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        with Session(self.database.get_engine()) as session:
            try:
                return session.exec(statement).all()
            except Exception as e:
                print(f"Error retrieving chat history: {e}")
                raise


chat = ChatHistoryService(DatabaseConnection())

for message in chat.get_history(
    user_id="test-user",
    conversation_id=UUID("12345678-1234-5678-1234-567812345678"),
):
    print(f"Retrieved message: {message.query} => {message.content}")