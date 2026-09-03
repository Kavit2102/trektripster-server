from trektripster import TrekTripster
from semantic_cache import SemanticCache
from langsmith import traceable

trek_tripster = TrekTripster()
cache = SemanticCache(threshold=0.85)

@traceable
def main():
    """
    CLI loop kept for local terminal use.
    """
    while True:
        query = input("Enter your question or 'quit' to exit: ")
        if query.lower() in ("quit", "exit"):
            break
        if not query:
            print("Please enter a valid question.")
            continue
        result = trek_tripster.answer_question(query)
        print(f"\nAnswer:\n{result}\n")
    
    # Show cache stats on exit
    # stats = cache.get_stats()
    # print(f"\nCache Statistics: {stats}")


if __name__ == "__main__":
    main()