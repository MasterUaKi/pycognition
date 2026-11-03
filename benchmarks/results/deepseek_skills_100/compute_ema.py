def compute_ema(values: list[float], alpha: float) -> dict:
    """
    Вычисляет массив экспоненциально сглаженных скользящих средних (EMA).

    Первое значение EMA инициализируется первым элементом входного массива.
    Для каждого последующего значения:
        ema[i] = alpha * values[i] + (1 - alpha) * ema[i - 1]

    :param values: входной массив числовых значений
    :param alpha: коэффициент сглаживания в диапазоне (0, 1]
    :return: словарь с ключами 'ema' (list[float]) и 'alpha' (float)
    :raises TypeError: если values не является списком или alpha не является числом
    :raises ValueError: если alpha вне диапазона (0, 1] или values пуст
    """
    if not isinstance(values, list):
        raise TypeError("values must be a list")
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise TypeError("alpha must be a number")
    if not (0.0 < alpha <= 1.0):
        raise ValueError("alpha must be in range (0, 1]")
    if len(values) == 0:
        raise ValueError("values must not be empty")

    ema: list[float] = []
    prev = float(values[0])
    ema.append(prev)
    for v in values[1:]:
        prev = alpha * float(v) + (1.0 - alpha) * prev
        ema.append(prev)

    return {"ema": ema, "alpha": float(alpha)}
