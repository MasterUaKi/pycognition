import pytest

from levenshtein_distance import levenshtein_distance


class TestLevenshteinDistance:
    def test_both_empty(self):
        assert levenshtein_distance("", "") == 0

    def test_first_empty(self):
        assert levenshtein_distance("", "abc") == 3

    def test_second_empty(self):
        assert levenshtein_distance("abc", "") == 3

    def test_identical_strings(self):
        assert levenshtein_distance("hello", "hello") == 0

    def test_single_insertion(self):
        assert levenshtein_distance("abc", "abcd") == 1

    def test_single_deletion(self):
        assert levenshtein_distance("abcd", "abc") == 1

    def test_single_substitution(self):
        assert levenshtein_distance("abc", "abd") == 1

    def test_classic_kitten_sitting(self):
        assert levenshtein_distance("kitten", "sitting") == 3

    def test_classic_flaw_lawn(self):
        assert levenshtein_distance("flaw", "lawn") == 2

    def test_completely_different(self):
        assert levenshtein_distance("abc", "xyz") == 3

    def test_symmetric(self):
        assert levenshtein_distance("kitten", "sitting") == levenshtein_distance("sitting", "kitten")

    def test_unicode_strings(self):
        assert levenshtein_distance("привет", "привед") == 1

    def test_single_characters_equal(self):
        assert levenshtein_distance("a", "a") == 0

    def test_single_characters_different(self):
        assert levenshtein_distance("a", "b") == 1

    def test_long_strings(self):
        s1 = "a" * 100
        s2 = "a" * 99 + "b"
        assert levenshtein_distance(s1, s2) == 1

    def test_type_error_on_non_string_first(self):
        with pytest.raises(TypeError):
            levenshtein_distance(123, "abc")

    def test_type_error_on_non_string_second(self):
        with pytest.raises(TypeError):
            levenshtein_distance("abc", None)

    def test_type_error_on_both_non_string(self):
        with pytest.raises(TypeError):
            levenshtein_distance(1, 2)
