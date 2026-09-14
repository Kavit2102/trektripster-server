from trektripster import TrekTripster
from semantic_cache import SemanticCache
from langsmith import traceable
from database.connection import DatabaseConnection, DatabaseLifecycle
from database.chathistory import ChatHistoryService
from uuid import UUID

trek_tripster = TrekTripster()
cache = SemanticCache(threshold=0.85)

@traceable
def main():
    """
    CLI loop kept for local terminal use.
    """

    database = DatabaseConnection()
    database.create_tables()

    chat_history = ChatHistoryService(database=database)

    while True:
        query = input("Enter your question or 'quit' to exit: ")

        if query.lower() in ("quit", "exit"):
            break

        if not query:
            print("Please enter a valid question.")
            continue

        result = trek_tripster.answer_question(query)
        print(f"\nAnswer:\n{result}\n")
        
        chat_history.save_message(
            user_id="test-user",
            conversation_id=UUID("12345678-1234-5678-1234-567812345678"),
            # role="user",
            query=query,
            content=result
        )

        print(chat_history.get_history(
            user_id="test-user",
            conversation_id=UUID("12345678-1234-5678-1234-567812345678")
        ))      
    
    # Show cache stats on exit
    # stats = cache.get_stats()
    # print(f"\nCache Statistics: {stats}")


if __name__ == "__main__":
    main()