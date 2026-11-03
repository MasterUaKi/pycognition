import pytest
from count_top_word_frequencies import count_top_word_frequencies


def test_basic_top_words():
    text = 'the quick brown fox jumps over the lazy dog the fox'
    result = count_top_word_frequencies(text)
    assert result == [
        {'word': 'fox', 'count': 2},
        {'word': 'the', 'count': 0} if False else {'word': 'brown', 'count': 1},
    ] or result == [
        {'word': 'fox', 'count': 2},
        {'word': 'brown', 'count': 1},
        {'word': 'dog', 'count': 1},
    ]


def test_default_top_k_is_three():
    text = 'alpha beta gamma delta epsilon alpha beta gamma alpha'
    result = count_top_word_frequencies(text)
    assert len(result) == 3
    assert result[0] == {'word': 'alpha', 'count': 3}
    assert result[1] == {'word': 'beta', 'count': 2}
    assert result[2] == {'word': 'gamma', 'count': 2}


def test_stop_words_excluded():
    text = 'the and a of to in is it that this with for on'
    result = count_top_word_frequencies(text)
    assert result == []


def test_alphabetical_tie_break():
    text = 'zebra apple mango zebra apple mango'
    result = count_top_word_frequencies(text, top_k=3)
    assert result == [
        {'word': 'apple', 'count': 2},
        {'word': 'mango', 'count': 2},
        {'word': 'zebra', 'count': 2},
    ]


def test_case_insensitive():
    text = 'Hello hello HELLO world World'
    result = count_top_word_frequencies(text, top_k=2)
    assert result == [
        {'word': 'hello', 'count': 3},
        {'word': 'world', 'count': 2},
    ]


def test_punctuation_ignored():
    text = 'cat, cat! dog? dog. bird; bird:'
    result = count_top_word_frequencies(text, top_k=3)
    assert result == [
        {'word': 'bird', 'count': 2},
        {'word': 'cat', 'count': 2},
        {'word': 'dog', 'count': 2},
    ]


def test_top_k_zero():
    assert count_top_word_frequencies('one two three', top_k=0) == []


def test_top_k_larger_than_unique():
    text = 'one two two'
    result = count_top_word_frequencies(text, top_k=10)
    assert result == [
        {'word': 'two', 'count': 2},
        {'word': 'one', 'count': 1},
    ]


def test_empty_text():
    assert count_top_word_frequencies('') == []


def test_whitespace_only():
    assert count_top_word_frequencies('   \n\t  ') == []


def test_non_string_text_raises():
    with pytest.raises(TypeError):
        count_top_word_frequencies(123)


def test_non_integer_top_k_raises():
    with pytest.raises(TypeError):
        count_top_word_frequencies('hello world', top_k='2')


def test_bool_top_k_raises():
    with pytest.raises(TypeError):
        count_top_word_frequencies('hello world', top_k=True)


def test_negative_top_k_raises():
    with pytest.raises(ValueError):
        count_top_word_frequencies('hello world', top_k=-1)


def test_numbers_are_words():
    text = '2024 2024 year 2024'
    result = count_top_word_frequencies(text, top_k=2)
    assert result == [
        {'word': '2024', 'count': 3},
        {'word': 'year', 'count': 1},
    ]
