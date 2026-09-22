from typing import Sequence
from uuid import UUID
from sqlmodel import Session, select
from database.models import MessageBase
from database.connection import DatabaseConnection


class Message:
    def __init__(self, database: DatabaseConnection) -> None:
        self.database = database

    def create_message(self, user_id: str | None, conversation_id: UUID, query: str | None, content: str) -> MessageBase:
        """
        Create a new message in the database.
        """
        new_message = MessageBase(user_id=user_id, conversation_id=conversation_id, query=query, content=content)

        with Session(self.database.get_engine()) as session:
            session.add(new_message)
            session.commit()
            session.refresh(new_message)
            return new_message

    def get_messages(self, user_id: str | None, conversation_id: UUID) -> Sequence[MessageBase]:
        """
        Retrieve messages from the database by user_id and conversation_id.
        """
        with Session(self.database.get_engine()) as session:
            statement = select(MessageBase).where(
                # MessageBase.user_id == user_id,
                MessageBase.conversation_id == conversation_id
            )
            result = session.exec(statement).all()

            if not result:
                raise ValueError(f"No messages found for user_id {user_id} and conversation_id {conversation_id}.")

            return result

    def get_message(self, message_id: UUID) -> MessageBase:
        """
        Retrieve a specific message by its ID.
        """
        with Session(self.database.get_engine()) as session:
            statement = select(MessageBase).where(MessageBase.message_id == message_id)
            result = session.exec(statement).first()

            if not result:
                raise ValueError(f"No message found with ID {message_id}.")

            return result

    def update_message(self, message_id: UUID, content: str) -> MessageBase:
        """
        Update content of a specific message by message id.
        """
        with Session(self.database.get_engine()) as session:
            message = session.get(MessageBase, message_id)

            if message is None:
                raise ValueError(f"No message found with ID {message_id}.")

            message.content = content
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

