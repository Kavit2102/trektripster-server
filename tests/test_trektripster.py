from types import SimpleNamespace
from unittest.mock import Mock

from services.trektripster import TrekTripster


def make_tripster():
    tripster = object.__new__(TrekTripster)
    tripster.cache = Mock()
    return tripster


def test_answer_question_returns_cached_answer_without_rag():
    tripster = make_tripster()
    tripster.cache.get_cached_answer.return_value = "Cached answer"
    tripster.get_rag_pipeline = Mock()

    result = tripster.answer_question("Question")

    assert result == "Cached answer"
    tripster.get_rag_pipeline.assert_not_called()
    tripster.cache.add_to_cache.assert_not_called()


def test_answer_question_generates_and_caches_new_answer():
    tripster = make_tripster()
    tripster.cache.get_cached_answer.return_value = None

    retriever = Mock()
    retriever.invoke.return_value = ["document"]
    tripster.get_rag_pipeline.return_value = retriever
    tripster.generate_answers.return_value = SimpleNamespace(
        content="Generated answer"
    )

    result = tripster.answer_question("Question")

    assert result == "Generated answer"
    retriever.invoke.assert_called_once_with("Question")
    tripster.cache.add_to_cache.assert_called_once_with(
        "Question",
        "Generated answer",
    )