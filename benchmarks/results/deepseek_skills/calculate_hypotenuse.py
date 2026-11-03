def calculate_hypotenuse(a: float, b: float) -> float:
    """Вычисляет гипотенузу прямоугольного треугольника по двум катетам.

    Использует теорему Пифагора: c = sqrt(a^2 + b^2).

    Аргументы:
        a (float): длина первого катета.
        b (float): длина второго катета.

    Возвращает:
        float: длина гипотенузы.

    Исключения:
        TypeError: если аргументы не являются числами (int или float).
        ValueError: если хотя бы один катет отрицателен.
    """
    if isinstance(a, bool) or isinstance(b, bool):
        raise TypeError("Аргументы должны быть числами, а не bool")
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Аргументы должны быть числами (int или float)")
    if a < 0 or b < 0:
        raise ValueError("Длины катетов не могут быть отрицательными")
    return (a * a + b * b) ** 0.5
