import math

import pytest

from compute_ema import compute_ema


def test_single_value():
    result = compute_ema([5.0], 0.5)
    assert result["ema"] == [5.0]
    assert result["alpha"] == 0.5


def test_alpha_one_returns_input():
    values = [1.0, 2.0, 3.0, 4.0]
    result = compute_ema(values, 1.0)
    assert result["ema"] == values
    assert result["alpha"] == 1.0


def test_known_sequence():
    values = [1.0, 2.0, 3.0, 4.0]
    alpha = 0.5
    result = compute_ema(values, alpha)
    expected = [1.0, 1.5, 2.25, 3.125]
    assert result["ema"] == pytest.approx(expected)
    assert result["alpha"] == alpha


def test_length_matches_input():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    result = compute_ema(values, 0.3)
    assert len(result["ema"]) == len(values)


def test_first_value_initialization():
    values = [7.5, 100.0, -3.0]
    result = compute_ema(values, 0.9)
    assert result["ema"][0] == 7.5


def test_constant_series():
    values = [4.0, 4.0, 4.0, 4.0]
    result = compute_ema(values, 0.7)
    assert result["ema"] == pytest.approx([4.0, 4.0, 4.0, 4.0])


def test_alpha_small():
    values = [0.0, 10.0, 10.0]
    alpha = 0.1
    result = compute_ema(values, alpha)
    expected = [0.0, 1.0, 1.9]
    assert result["ema"] == pytest.approx(expected)


def test_negative_values():
    values = [-1.0, -2.0, -3.0]
    alpha = 0.5
    result = compute_ema(values, alpha)
    expected = [-1.0, -1.5, -2.25]
    assert result["ema"] == pytest.approx(expected)


def test_alpha_zero_raises():
    with pytest.raises(ValueError):
        compute_ema([1.0, 2.0], 0.0)


def test_alpha_negative_raises():
    with pytest.raises(ValueError):
        compute_ema([1.0, 2.0], -0.1)


def test_alpha_greater_than_one_raises():
    with pytest.raises(ValueError):
        compute_ema([1.0, 2.0], 1.5)


def test_empty_values_raises():
    with pytest.raises(ValueError):
        compute_ema([], 0.5)


def test_values_not_list_raises():
    with pytest.raises(TypeError):
        compute_ema((1.0, 2.0), 0.5)


def test_alpha_not_number_raises():
    with pytest.raises(TypeError):
        compute_ema([1.0, 2.0], "0.5")


def test_alpha_bool_raises():
    with pytest.raises(TypeError):
        compute_ema([1.0, 2.0], True)


def test_return_types():
    result = compute_ema([1, 2, 3], 0.5)
    assert isinstance(result, dict)
    assert isinstance(result["ema"], list)
    assert all(isinstance(x, float) for x in result["ema"])
    assert isinstance(result["alpha"], float)


def test_determinism():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    r1 = compute_ema(values, 0.4)
    r2 = compute_ema(values, 0.4)
    assert r1 == r2
