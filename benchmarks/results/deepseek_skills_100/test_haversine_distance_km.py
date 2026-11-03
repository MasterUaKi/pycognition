import math

import pytest

from haversine_distance_km import haversine_distance_km


def test_same_point_returns_zero():
    assert haversine_distance_km(0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0, abs=1e-9)


def test_same_point_nonzero_coords():
    assert haversine_distance_km(55.7558, 37.6173, 55.7558, 37.6173) == pytest.approx(0.0, abs=1e-9)


def test_equator_one_degree_longitude():
    # На экваторе 1 градус долготы ~ 111.195 км (R * pi / 180).
    expected = 6371.0088 * math.pi / 180.0
    assert haversine_distance_km(0.0, 0.0, 0.0, 1.0) == pytest.approx(expected, rel=1e-9)


def test_meridian_one_degree_latitude():
    # Вдоль меридиана 1 градус широты ~ 111.195 км.
    expected = 6371.0088 * math.pi / 180.0
    assert haversine_distance_km(0.0, 0.0, 1.0, 0.0) == pytest.approx(expected, rel=1e-9)


def test_antipodal_points_half_circumference():
    # Противоположные точки: расстояние = pi * R.
    expected = math.pi * 6371.0088
    assert haversine_distance_km(0.0, 0.0, 0.0, 180.0) == pytest.approx(expected, rel=1e-9)


def test_antipodal_poles():
    expected = math.pi * 6371.0088
    assert haversine_distance_km(90.0, 0.0, -90.0, 0.0) == pytest.approx(expected, rel=1e-9)


def test_symmetry():
    d1 = haversine_distance_km(10.0, 20.0, 30.0, 40.0)
    d2 = haversine_distance_km(30.0, 40.0, 10.0, 20.0)
    assert d1 == pytest.approx(d2, rel=1e-12)


def test_moscow_to_spb():
    # Москва (55.7558, 37.6173) — Санкт-Петербург (59.9343, 30.3351).
    # Известное расстояние ~ 634-635 км.
    d = haversine_distance_km(55.7558, 37.6173, 59.9343, 30.3351)
    assert d == pytest.approx(634.0, abs=5.0)


def test_london_to_paris():
    # Лондон (51.5074, -0.1278) — Париж (48.8566, 2.3522). ~ 343.5 км.
    d = haversine_distance_km(51.5074, -0.1278, 48.8566, 2.3522)
    assert d == pytest.approx(343.5, abs=2.0)


def test_new_york_to_los_angeles():
    # Нью-Йорк (40.7128, -74.0060) — Лос-Анджелес (34.0522, -118.2437). ~ 3936 км.
    d = haversine_distance_km(40.7128, -74.0060, 34.0522, -118.2437)
    assert d == pytest.approx(3936.0, abs=20.0)


def test_returns_float():
    result = haversine_distance_km(0.0, 0.0, 1.0, 1.0)
    assert isinstance(result, float)


def test_non_negative():
    assert haversine_distance_km(-45.0, -90.0, 45.0, 90.0) >= 0.0


def test_longitude_wraparound():
    # 179 и -179 градусов долготы — 2 градуса разницы.
    expected = 6371.0088 * math.radians(2.0)
    assert haversine_distance_km(0.0, 179.0, 0.0, -179.0) == pytest.approx(expected, rel=1e-9)


def test_triangle_inequality():
    a = haversine_distance_km(0.0, 0.0, 10.0, 10.0)
    b = haversine_distance_km(10.0, 10.0, 20.0, 20.0)
    c = haversine_distance_km(0.0, 0.0, 20.0, 20.0)
    assert c <= a + b + 1e-9
