from mailbox import Message
from typing import Sequence
from uuid import UUID
from sqlmodel import Session, select
from database.models import ConversationBase
from database.connection import DatabaseConnection
# from database.user import User

class Conversation:
    """
    Handles chat message persistence and retrieval.
    """

    def __init__(self, database: DatabaseConnection) -> None:
        self.database = database

    def create_conversation(self, 
        user_id: str,
        conversation_id: UUID, 
        title: str
    ) -> None:
        """
        Create a new conversation in the database.
        """

        new_convo = ConversationBase(user_id=user_id, conversation_id=conversation_id, title=title)

        with Session(self.database.get_engine()) as session:
            try:
                session.add(new_convo)
                session.commit()
                print("Conversation created !!")
            except Exception as e:
                session.rollback()
                print(f"Error creating conversation: {e}")
                raise

    def get_conversation(self, user_id: str | None = None) -> Sequence[ConversationBase]:
        """
        Retrieve conversation messages from the database by user_id and conversation_id.
        """
        try:

            with Session(self.database.get_engine()) as session:
                statement = select(ConversationBase)

                if user_id is not None:
                    statement = statement.where(ConversationBase.user_id == user_id)

                    result = session.exec(statement.order_by(ConversationBase.created_at)).all()
                    return result

                return []

        except Exception as e:
            session.rollback()
            print(f"Error getting conversations: {e}")
            raise

# DatabaseConnection().create_tables()
# convo = Conversation(DatabaseConnection())

# convo.create_conversation(
#     conversation_id=UUID("12345678-1234-5678-1234-567812345678"),
#     user_id="user_123",
#     title="New Convo"
# )

# print(convo.get_conversation(title="New Convo"))

