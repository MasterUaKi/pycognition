def calculate_ema(values, alpha=0.3):
    """
    Вычисляет экспоненциальное скользящее среднее (EMA) для ряда числовых значений.

    :param values: list[float] — входной ряд чисел
    :param alpha: float — коэффициент сглаживания (0 < alpha <= 1), по умолчанию 0.3
    :return: list[float] — ряд значений EMA той же длины, что и values
    """
    if not isinstance(values, list):
        raise TypeError("values должен быть списком")
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool):
        raise TypeError("alpha должен быть числом")
    if not (0 < alpha <= 1):
        raise ValueError("alpha должен удовлетворять условию 0 < alpha <= 1")
    for v in values:
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise TypeError("все элементы values должны быть числами")

    if not values:
        return []

    ema = [float(values[0])]
    for v in values[1:]:
        ema.append(alpha * float(v) + (1 - alpha) * ema[-1])
    return ema
