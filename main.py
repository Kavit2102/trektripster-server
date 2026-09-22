from services.trektripster import TrekTripster
# from langsmith import traceable
from database.connection import DatabaseConnection
from database.conversation import Conversation
from services.chat_service import answer_and_persist
from uuid import uuid4
import asyncio

# Creates the main trip-answering object used to answer user questions.
trek_tripster = TrekTripster()

# @traceable
# Defines the main chat loop that runs the command-line application.
async def main():
    # Creates a database connection and ensures all necessary database tables exist.
    database = DatabaseConnection()
    database.create_tables()

    # Gets a conversation service connected to the database.
    conversation_service = Conversation(database)
    # Looks for an existing conversation for this user.
    conversation = conversation_service.get_conversation(user_id="")

    # If no conversation exists, create a new one with a unique ID.
    if not conversation:
        # Generates a unique ID for the new conversation.
        conversation_id = uuid4()
        # Saves the new conversation record to the database.
        conversation_service.create_conversation(
            user_id="",
            conversation_id=conversation_id,
            title="New Convo",
        )
    else:
        # Uses the existing conversation ID if a conversation already exists.
        conversation_id = conversation[0].conversation_id

    # Runs an infinite loop so the user can keep asking questions.
    while True:
        # Prompts the user to type a question or quit the program.
        query = input("Enter your question or 'quit' to exit: ")

        # Exits the loop when the user types quit or exit.
        if query.lower() in ("quit", "exit"):
            break

        # Rejects empty input before sending it to the chatbot.
        if not query:
            # Prints a message telling the user to enter a valid question.
            print("Please enter a valid question.")
            continue

        # Calls the answer_and_persist workflow to generate and save the answer.
        result = await answer_and_persist(
            database=database,
            conversation_id=conversation_id,
            query=query,
        )

        # Displays the answer returned by the chatbot.
        print(f"\nAnswer:\n{result}\n")


# Ensures the main function runs only when this file is executed directly.
if __name__ == "__main__":
    # Starts the async event loop and runs the CLI application.
    asyncio.run(main())