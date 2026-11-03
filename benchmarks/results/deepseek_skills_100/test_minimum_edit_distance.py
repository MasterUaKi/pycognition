import pytest
from minimum_edit_distance import minimum_edit_distance


def test_both_empty():
    assert minimum_edit_distance("", "") == 0


def test_first_empty():
    assert minimum_edit_distance("", "abc") == 3


def test_second_empty():
    assert minimum_edit_distance("abc", "") == 3


def test_identical_strings():
    assert minimum_edit_distance("kitten", "kitten") == 0


def test_classic_kitten_sitting():
    assert minimum_edit_distance("kitten", "sitting") == 3


def test_single_substitution():
    assert minimum_edit_distance("a", "b") == 1


def test_single_insertion():
    assert minimum_edit_distance("a", "ab") == 1


def test_single_deletion():
    assert minimum_edit_distance("ab", "a") == 1


def test_completely_different():
    assert minimum_edit_distance("abc", "xyz") == 3


def test_symmetric():
    assert minimum_edit_distance("flaw", "lawn") == minimum_edit_distance("lawn", "flaw")


def test_unicode_strings():
    assert minimum_edit_distance("привет", "привет") == 0
    assert minimum_edit_distance("привет", "привт") == 1


def test_long_strings():
    a = "a" * 100
    b = "b" * 100
    assert minimum_edit_distance(a, b) == 100


def test_type_error_non_string():
    with pytest.raises(TypeError):
        minimum_edit_distance(123, "abc")
    with pytest.raises(TypeError):
        minimum_edit_distance("abc", None)


def test_whitespace_strings():
    assert minimum_edit_distance(" ", "") == 1
    assert minimum_edit_distance("a b", "ab") == 1
