from datetime import datetime, UTC, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

# class UserBase(SQLModel, table=True):

#     __tablename__ = "users"

#     # id: UUID = Field(
#     # )

#     user_id: str = Field(
#         default_factory=uuid4,
#         primary_key=True,
#         index=True,
#         max_length=255,
#         unique=True
#     )

#     email: str = Field(
#         index=True,
#         max_length=255,
#         unique=True,
#     )

#     created_at: datetime = Field(
#         default_factory=lambda: datetime.now(timezone.utc),
#         index=True,
#     )

class ConversationBase(SQLModel, table=True):
    
    __tablename__ = "conversations"

    # id: UUID = Field(
    #     default_factory=uuid4,
    # )

    conversation_id: UUID = Field(
        default_factory=uuid4,
        index=True,
        max_length=255,
        unique=True,
        primary_key=True,
    )

    user_id: str = Field(
        index=True,
        # foreign_key="users.user_id",
        max_length=255,
    )

    title: str = Field(
        default="New Convo",
        max_length=25
        # unique=True
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
    )

class MessageBase(SQLModel, table=True):

    __tablename__ = "messages"

    message_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        unique=True,
    )

    # user_id: str = Field(
    #     index=True,
    #     max_length=255,
    # )

    conversation_id: UUID = Field(
        index=True,
        foreign_key="conversations.conversation_id",
        max_length=255
    )

    query: str = Field(
        max_length=1000
    )

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
    )