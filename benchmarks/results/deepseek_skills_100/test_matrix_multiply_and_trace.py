import pytest
from matrix_multiply_and_trace import matrix_multiply_and_trace


def test_square_matrices():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    result = matrix_multiply_and_trace(a, b)
    assert result["product"] == [[19, 22], [43, 50]]
    assert result["trace"] == 69


def test_identity_matrix():
    a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    result = matrix_multiply_and_trace(a, identity)
    assert result["product"] == a
    assert result["trace"] == 15


def test_rectangular_matrices():
    a = [[1, 2, 3], [4, 5, 6]]  # 2x3
    b = [[7, 8], [9, 10], [11, 12]]  # 3x2
    result = matrix_multiply_and_trace(a, b)
    assert result["product"] == [[58, 64], [139, 154]]
    assert result["trace"] == 212


def test_non_square_trace():
    a = [[1, 2], [3, 4], [5, 6]]  # 3x2
    b = [[1, 0, 1], [0, 1, 0]]  # 2x3
    result = matrix_multiply_and_trace(a, b)
    assert result["product"] == [[1, 2, 1], [3, 4, 3], [5, 6, 5]]
    assert result["trace"] == 10


def test_float_values():
    a = [[0.5, 1.5], [2.5, 3.5]]
    b = [[1.0, 0.0], [0.0, 1.0]]
    result = matrix_multiply_and_trace(a, b)
    assert result["product"] == [[0.5, 1.5], [2.5, 3.5]]
    assert result["trace"] == 4.0


def test_single_element():
    a = [[3.0]]
    b = [[4.0]]
    result = matrix_multiply_and_trace(a, b)
    assert result["product"] == [[12.0]]
    assert result["trace"] == 12.0


def test_incompatible_dimensions():
    a = [[1, 2, 3]]  # 1x3
    b = [[1, 2], [3, 4]]  # 2x2
    with pytest.raises(ValueError):
        matrix_multiply_and_trace(a, b)


def test_empty_matrix():
    with pytest.raises(ValueError):
        matrix_multiply_and_trace([], [[1]])
    with pytest.raises(ValueError):
        matrix_multiply_and_trace([[1]], [])


def test_ragged_matrix():
    with pytest.raises(ValueError):
        matrix_multiply_and_trace([[1, 2], [3]], [[1], [2]])
    with pytest.raises(ValueError):
        matrix_multiply_and_trace([[1], [2]], [[1, 2], [3]])


def test_non_numeric_entries():
    with pytest.raises(TypeError):
        matrix_multiply_and_trace([[1, "a"]], [[1], [2]])
    with pytest.raises(TypeError):
        matrix_multiply_and_trace([[1]], [["b"]])


def test_non_list_input():
    with pytest.raises(TypeError):
        matrix_multiply_and_trace("not a matrix", [[1]])
    with pytest.raises(TypeError):
        matrix_multiply_and_trace([[1]], 42)


def test_bool_rejected():
    with pytest.raises(TypeError):
        matrix_multiply_and_trace([[True]], [[1]])
