def minimum_edit_distance(a: str, b: str) -> int:
    """
    Вычисляет минимальное редакционное расстояние (расстояние Левенштейна)
    между двумя строками с единичными стоимостями вставки, удаления и замены.

    :param a: первая строка
    :param b: вторая строка
    :return: минимальное количество операций редактирования
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("Аргументы 'a' и 'b' должны быть строками")

    len_a = len(a)
    len_b = len(b)

    # Оптимизация: храним только две строки матрицы
    if len_a == 0:
        return len_b
    if len_b == 0:
        return len_a

    previous_row = list(range(len_b + 1))

    for i in range(1, len_a + 1):
        current_row = [i] + [0] * len_b
        char_a = a[i - 1]
        for j in range(1, len_b + 1):
            cost = 0 if char_a == b[j - 1] else 1
            current_row[j] = min(
                previous_row[j] + 1,        # удаление
                current_row[j - 1] + 1,     # вставка
                previous_row[j - 1] + cost  # замена
            )
        previous_row = current_row

    return previous_row[len_b]
