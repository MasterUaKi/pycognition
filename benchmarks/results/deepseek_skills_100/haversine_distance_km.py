import math


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Вычисляет расстояние по большому кругу между двумя точками на сфере.

    Использует формулу гаверсинуса. Радиус Земли принят равным 6371.0088 км
    (средний радиус Земли по IUGG).

    Аргументы:
        lat1: широта первой точки в градусах.
        lon1: долгота первой точки в градусах.
        lat2: широта второй точки в градусах.
        lon2: долгота второй точки в градусах.

    Возвращает:
        Расстояние между точками в километрах (float).
    """
    earth_radius_km = 6371.0088

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    sin_dphi = math.sin(delta_phi / 2.0)
    sin_dlambda = math.sin(delta_lambda / 2.0)

    a = sin_dphi * sin_dphi + math.cos(phi1) * math.cos(phi2) * sin_dlambda * sin_dlambda
    # Ограничение для защиты от ошибок округления при a чуть больше 1.
    if a > 1.0:
        a = 1.0
    elif a < 0.0:
        a = 0.0

    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return earth_radius_km * c
