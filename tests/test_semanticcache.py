from types import SimpleNamespace
from unittest.mock import Mock

from services.semanticcache import SemanticCache


def make_cache(threshold=0.85):
    cache = object.__new__(SemanticCache)
    cache.threshold = threshold
    cache.get_embedding = Mock(return_value=[0.1, 0.2])
    return cache


def test_get_cached_answer_returns_answer_above_threshold():
    cache = make_cache()
    cache.search_cache.return_value = Mock(return_value=[
        SimpleNamespace(
            score=0.90,
            payload={"response_text": "Cached answer"},
        )
    ])

    result = cache.get_cached_answer("Question")

    assert result == "Cached answer"


def test_get_cached_answer_returns_none_below_threshold():
    cache = make_cache()
    cache.search_cache.return_value = [
        SimpleNamespace(
            score=0.84,
            payload={"response_text": "Cached answer"},
        )
    ]

    result = cache.get_cached_answer("Question")

    assert result is None


def test_get_cached_answer_returns_none_when_cache_is_empty():
    cache = make_cache()
    cache.search_cache.return_value = []

    result = cache.get_cached_answer("Question")

    assert result is None