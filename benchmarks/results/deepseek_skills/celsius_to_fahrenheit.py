def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Конвертирует температуру из градусов Цельсия в градусы Фаренгейта.

    Формула: F = C * 9/5 + 32

    :param celsius: Температура в градусах Цельсия (float).
    :return: Температура в градусах Фаренгейта (float).
    """
    return celsius * 9.0 / 5.0 + 32.0
