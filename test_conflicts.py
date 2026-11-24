from datetime import datetime

from stride.conflicts import find_conflicts
from stride.models import Event


def ev(id, sh, sm, eh, em):
    return Event(id, id, datetime(2026, 11, 24, sh, sm), datetime(2026, 11, 24, eh, em))


def test_overlap_detected():
    pairs = find_conflicts([ev("a", 9, 0, 10, 30), ev("b", 10, 0, 11, 0)])
    assert [(a.id, b.id) for a, b in pairs] == [("a", "b")]


def test_back_to_back_is_not_a_conflict():
    assert find_conflicts([ev("a", 9, 0, 10, 0), ev("b", 10, 0, 11, 0)]) == []


def test_unsorted_input_and_multiple_overlaps():
    pairs = find_conflicts([ev("c", 9, 30, 10, 30), ev("a", 9, 0, 11, 0), ev("b", 12, 0, 13, 0)])
    assert {(a.id, b.id) for a, b in pairs} == {("a", "c")}


def test_empty():
    assert find_conflicts([]) == []
