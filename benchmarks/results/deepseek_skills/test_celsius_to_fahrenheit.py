import pytest
from celsius_to_fahrenheit import celsius_to_fahrenheit


@pytest.mark.parametrize(
    "celsius, expected",
    [
        (0.0, 32.0),
        (100.0, 212.0),
        (-40.0, -40.0),
        (37.0, 98.6),
        (-273.15, -459.67),
        (25.0, 77.0),
        (1.0, 33.8),
        (-10.0, 14.0),
    ],
)
def test_celsius_to_fahrenheit_known_values(celsius, expected):
    result = celsius_to_fahrenheit(celsius)
    assert isinstance(result, float)
    assert result == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_celsius_to_fahrenheit_returns_float():
    result = celsius_to_fahrenheit(0)
    assert isinstance(result, float)


def test_celsius_to_fahrenheit_identity_minus40():
    assert celsius_to_fahrenheit(-40.0) == pytest.approx(-40.0)


def test_celsius_to_fahrenheit_linearity():
    # Проверка линейности: F(C + d) - F(C) = d * 9/5
    c = 12.5
    d = 7.5
    delta_f = celsius_to_fahrenheit(c + d) - celsius_to_fahrenheit(c)
    assert delta_f == pytest.approx(d * 9.0 / 5.0)
