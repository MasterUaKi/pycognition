import pytest
from calculate_ema import calculate_ema


def test_empty_list():
    assert calculate_ema([]) == []


def test_single_value():
    assert calculate_ema([5.0]) == [5.0]


def test_default_alpha():
    result = calculate_ema([1.0, 2.0, 3.0])
    expected = [1.0, 1.3, 1.81]
    assert result == pytest.approx(expected)


def test_custom_alpha():
    result = calculate_ema([1.0, 2.0, 3.0], alpha=0.5)
    expected = [1.0, 1.5, 2.25]
    assert result == pytest.approx(expected)


def test_alpha_one():
    result = calculate_ema([1.0, 2.0, 3.0], alpha=1.0)
    assert result == [1.0, 2.0, 3.0]


def test_length_preserved():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = calculate_ema(values, alpha=0.2)
    assert len(result) == len(values)


def test_invalid_alpha_zero():
    with pytest.raises(ValueError):
        calculate_ema([1.0, 2.0], alpha=0.0)


def test_invalid_alpha_negative():
    with pytest.raises(ValueError):
        calculate_ema([1.0, 2.0], alpha=-0.1)


def test_invalid_alpha_greater_than_one():
    with pytest.raises(ValueError):
        calculate_ema([1.0, 2.0], alpha=1.1)


def test_invalid_values_type():
    with pytest.raises(TypeError):
        calculate_ema("not a list")


def test_invalid_element_type():
    with pytest.raises(TypeError):
        calculate_ema([1.0, "2", 3.0])


def test_invalid_alpha_type():
    with pytest.raises(TypeError):
        calculate_ema([1.0, 2.0], alpha="0.3")


def test_bool_alpha_rejected():
    with pytest.raises(TypeError):
        calculate_ema([1.0, 2.0], alpha=True)


def test_bool_element_rejected():
    with pytest.raises(TypeError):
        calculate_ema([1.0, True, 3.0])


def test_integer_values():
    result = calculate_ema([1, 2, 3], alpha=0.5)
    expected = [1.0, 1.5, 2.25]
    assert result == pytest.approx(expected)
