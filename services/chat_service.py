import asyncio
from database.connection import DatabaseConnection
from database.message import Message
from services.trektripster import TrekTripster

async def answer_and_persist(
    user_id: str,
    database: DatabaseConnection,
    trek_tripster: TrekTripster,
    conversation_id: str,
    query: str,
):
    # Creates a message service object for working with stored messages.
    message_service = Message(database)

    # Starts a background task that saves the user's original prompt in the DB
    # with an empty content field before the answer is generated.
    create_task = asyncio.create_task(
        asyncio.to_thread(
            message_service.create_message,
            user_id=user_id,
            conversation_id=conversation_id,
            query=query,
            content="",
        )
    )

    # Starts another background task to call the AI answer function for the question.
    answer_task = asyncio.create_task(
        asyncio.to_thread(trek_tripster.answer_question, query)
    )

    # Waits for both tasks to finish and stores both the message record and answer.
    message, answer = await asyncio.gather(create_task, answer_task)

    # Updates the saved message with the final answer produced by the assistant.
    await asyncio.to_thread(
        message_service.update_message,
        message_id=message.message_id,
        content=answer,
    )

    # Returns the generated answer so the caller can print it to the console.
    return answer