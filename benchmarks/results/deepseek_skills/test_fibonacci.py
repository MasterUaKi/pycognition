import pytest
from fibonacci import fibonacci


def test_fibonacci_zero():
    assert fibonacci(0) == 0


def test_fibonacci_one():
    assert fibonacci(1) == 1


def test_fibonacci_two():
    assert fibonacci(2) == 1


def test_fibonacci_three():
    assert fibonacci(3) == 2


def test_fibonacci_ten():
    assert fibonacci(10) == 55


def test_fibonacci_twenty():
    assert fibonacci(20) == 6765


def test_fibonacci_large():
    assert fibonacci(50) == 12586269025


def test_fibonacci_negative_raises():
    with pytest.raises(ValueError):
        fibonacci(-1)


def test_fibonacci_float_raises():
    with pytest.raises(TypeError):
        fibonacci(3.5)


def test_fibonacci_string_raises():
    with pytest.raises(TypeError):
        fibonacci("5")


def test_fibonacci_bool_raises():
    with pytest.raises(TypeError):
        fibonacci(True)


def test_fibonacci_none_raises():
    with pytest.raises(TypeError):
        fibonacci(None)
