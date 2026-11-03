import pytest
from multiply_matrices_and_trace import multiply_matrices_and_trace


def test_identity_matrices():
    a = [[1, 0], [0, 1]]
    b = [[1, 0], [0, 1]]
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == [[1, 0], [0, 1]]
    assert result['trace'] == 2


def test_simple_2x2():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == [[19, 22], [43, 50]]
    assert result['trace'] == 69


def test_3x3():
    a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    b = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == [[30, 24, 18], [84, 69, 54], [138, 114, 90]]
    assert result['trace'] == 189


def test_1x1():
    a = [[5]]
    b = [[7]]
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == [[35]]
    assert result['trace'] == 35


def test_empty_matrices():
    a = []
    b = []
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == []
    assert result['trace'] == 0


def test_negative_numbers():
    a = [[-1, 2], [3, -4]]
    b = [[5, -6], [-7, 8]]
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == [[-19, 22], [43, -50]]
    assert result['trace'] == -69


def test_float_numbers():
    a = [[1.5, 2.5], [3.5, 4.5]]
    b = [[0.5, 1.5], [2.5, 3.5]]
    result = multiply_matrices_and_trace(a, b)
    assert result['product'] == [[7.0, 11.0], [13.0, 21.0]]
    assert result['trace'] == 28.0


def test_non_square_matrix_a():
    a = [[1, 2, 3], [4, 5, 6]]
    b = [[1, 2], [3, 4]]
    with pytest.raises(ValueError, match='matrix_a must be a square matrix'):
        multiply_matrices_and_trace(a, b)


def test_non_square_matrix_b():
    a = [[1, 2], [3, 4]]
    b = [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError, match='matrix_b must be a square matrix of the same size as matrix_a'):
        multiply_matrices_and_trace(a, b)


def test_mismatched_sizes():
    a = [[1, 2], [3, 4]]
    b = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    with pytest.raises(ValueError, match='matrix_b must be a square matrix of the same size as matrix_a'):
        multiply_matrices_and_trace(a, b)
