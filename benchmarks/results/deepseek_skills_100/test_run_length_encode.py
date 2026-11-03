import pytest
from run_length_encode import run_length_encode


def test_empty_string():
    assert run_length_encode("") == ""


def test_single_character():
    assert run_length_encode("a") == "a1"


def test_all_same_characters():
    assert run_length_encode("aaaa") == "a4"


def test_no_repeats():
    assert run_length_encode("abc") == "a1b1c1"


def test_mixed_repeats():
    assert run_length_encode("aaabbc") == "a3b2c1"


def test_repeats_at_ends():
    assert run_length_encode("aabbbcc") == "a2b3c2"


def test_single_repeat_in_middle():
    assert run_length_encode("abbbc") == "a1b3c1"


def test_digits_and_letters():
    assert run_length_encode("11122a") == "1322a1"


def test_special_characters():
    assert run_length_encode("!!??") == "!2?2"


def test_whitespace():
    assert run_length_encode("  \t\t") == " 2\t2"


def test_long_run():
    assert run_length_encode("a" * 100) == "a100"


def test_type_error_on_non_string():
    with pytest.raises(TypeError):
        run_length_encode(123)


def test_type_error_on_none():
    with pytest.raises(TypeError):
        run_length_encode(None)
