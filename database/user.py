# from typing import Sequence
# from uuid import UUID
from sqlmodel import Session, select
# from models import Message
from database.connection import DatabaseConnection
from database.models import UserBase

class User:
    """
    Handles authenticated users history.
    """

    def __init__(self, database: DatabaseConnection) -> None:
        self.database = database

    def create_user(self, user_id: str, email: str) -> None:
        """
        Create a new user in the database.
        """

        new_user = UserBase(user_id=user_id, email=email)

        with Session(self.database.get_engine()) as session:
            try:
                session.add(new_user)
                session.commit()
                print("User created !!")
            except Exception as e:
                session.rollback()
                print(f"Error creating user: {e}")
                raise

    def get_user(self, user_id: str) -> UserBase:
        """
        Retrieve a user from the database by user_id.
        """

        with Session(self.database.get_engine()) as session:
            statement = select(UserBase).where(UserBase.user_id == user_id)
            result = session.exec(statement).first()

            if result is None:
                raise ValueError(f"User with user_id {user_id} not found.")

            return result.user_id

# user = User(DatabaseConnection())

# print(user.get_user(user_id="user_123"))
