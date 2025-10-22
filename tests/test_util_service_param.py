from __future__ import annotations

import sys
from types import ModuleType

import pytest


# Provide a lightweight dummy 'requests' module if not installed so tests can be imported
if "requests" not in sys.modules:
    sys.modules["requests"] = ModuleType("requests")

import src.service.util_service as util


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 5, True),
        (5, 1, True),
        (2, 2, True),
    ],
)
def test_random_number_bounds(a, b, expected):
    # deterministic check: result is within bounds
    for _ in range(10):
        r = util.random_number(a, b)
        assert min(a, b) <= r <= max(a, b)


@pytest.mark.parametrize(
    "arr,expected",
    [
        (["a", "b", "c"], {"a", "b", "c"}),
        ([], set()),
    ],
)
def test_random_word_from_list(arr, expected):
    if not arr:
        # when empty, random.choice will raise; util.random_word handles None but not empty list
        with pytest.raises(IndexError):
            util.random_word(arr)
        return
    val = util.random_word(arr)
    assert val in expected


def test_format_unix_time():
    assert util.format_unix_time(1698123456).startswith("<t:")
