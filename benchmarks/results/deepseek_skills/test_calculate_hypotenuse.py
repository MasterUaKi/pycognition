import math

import pytest

from calculate_hypotenuse import calculate_hypotenuse


def test_three_four_five():
    assert calculate_hypotenuse(3.0, 4.0) == pytest.approx(5.0)


def test_equal_legs():
    assert calculate_hypotenuse(1.0, 1.0) == pytest.approx(math.sqrt(2.0))


def test_zero_leg():
    assert calculate_hypotenuse(0.0, 5.0) == pytest.approx(5.0)
    assert calculate_hypotenuse(5.0, 0.0) == pytest.approx(5.0)


def test_both_zero():
    assert calculate_hypotenuse(0.0, 0.0) == pytest.approx(0.0)


def test_integer_inputs():
    assert calculate_hypotenuse(6, 8) == pytest.approx(10.0)


def test_large_values():
    assert calculate_hypotenuse(1e150, 1e150) == pytest.approx(math.sqrt(2.0) * 1e150)


def test_small_values():
    assert calculate_hypotenuse(1e-150, 1e-150) == pytest.approx(math.sqrt(2.0) * 1e-150)


def test_negative_leg_raises():
    with pytest.raises(ValueError):
        calculate_hypotenuse(-1.0, 2.0)
    with pytest.raises(ValueError):
        calculate_hypotenuse(2.0, -1.0)


def test_non_numeric_raises():
    with pytest.raises(TypeError):
        calculate_hypotenuse("3", 4.0)
    with pytest.raises(TypeError):
        calculate_hypotenuse(3.0, None)


def test_bool_raises():
    with pytest.raises(TypeError):
        calculate_hypotenuse(True, 4.0)
    with pytest.raises(TypeError):
        calculate_hypotenuse(3.0, False)


def test_returns_float():
    result = calculate_hypotenuse(3, 4)
    assert isinstance(result, float)
