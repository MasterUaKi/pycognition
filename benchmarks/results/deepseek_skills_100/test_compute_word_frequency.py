import pytest
from compute_word_frequency import compute_word_frequency


def test_basic_counts():
    result = compute_word_frequency('the cat and the dog', stop_words=['the', 'and'])
    assert result == {'cat': 1, 'dog': 1}


def test_default_stop_words():
    result = compute_word_frequency('The quick brown fox jumps over the lazy dog')
    assert 'the' not in result
    assert result['quick'] == 1
    assert result['fox'] == 1


def test_sorting_by_frequency_then_alpha():
    text = 'b a b c a b c d'
    result = compute_word_frequency(text, stop_words=[])
    keys = list(result.keys())
    assert keys == ['b', 'a', 'c', 'd']
    assert result['b'] == 3
    assert result['a'] == 2
    assert result['c'] == 2
    assert result['d'] == 1


def test_top_k():
    text = 'a b b c c c d d d d'
    result = compute_word_frequency(text, stop_words=[], top_k=2)
    assert result == {'d': 4, 'c': 3}


def test_top_k_zero():
    assert compute_word_frequency('a b c', stop_words=[], top_k=0) == {}


def test_empty_text():
    assert compute_word_frequency('', stop_words=[]) == {}


def test_punctuation_and_case():
    result = compute_word_frequency('Hello, hello! HELLO world.', stop_words=[])
    assert result == {'hello': 3, 'world': 1}


def test_apostrophes_and_numbers():
    result = compute_word_frequency("don't stop 42 times", stop_words=[])
    assert result == {"don't": 1, 'stop': 1, '42': 1, 'times': 1}


def test_stop_words_case_insensitive():
    result = compute_word_frequency('The THE the cat', stop_words=['the'])
    assert result == {'cat': 1}


def test_invalid_text_type():
    with pytest.raises(TypeError):
        compute_word_frequency(123)


def test_invalid_stop_words_type():
    with pytest.raises(TypeError):
        compute_word_frequency('hello', stop_words='the')


def test_invalid_stop_words_element():
    with pytest.raises(TypeError):
        compute_word_frequency('hello', stop_words=['the', 1])


def test_invalid_top_k_type():
    with pytest.raises(TypeError):
        compute_word_frequency('hello', top_k='2')


def test_invalid_top_k_bool():
    with pytest.raises(TypeError):
        compute_word_frequency('hello', top_k=True)


def test_negative_top_k():
    with pytest.raises(ValueError):
        compute_word_frequency('hello', top_k=-1)


def test_deterministic_output():
    text = 'one two two three three three four four four four'
    r1 = compute_word_frequency(text, stop_words=[])
    r2 = compute_word_frequency(text, stop_words=[])
    assert r1 == r2
    assert list(r1.items()) == list(r2.items())
