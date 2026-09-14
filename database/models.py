from datetime import datetime, UTC, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class Message(SQLModel, table=True):

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    user_id: str = Field(
        index=True,
        max_length=255,
    )

    conversation_id: UUID = Field(
        index=True,
    )

    # role: str = Field(
    #     max_length=20,
    # )

    query: str = Field(
        max_length=1000
    )

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
    )