def levenshtein_distance(s1: str, s2: str) -> int:
    """Вычисляет расстояние Левенштейна между двумя строками.

    Расстояние Левенштейна — минимальное количество односимвольных правок
    (вставка, удаление, замена), необходимых для преобразования s1 в s2.

    Args:
        s1: Первая строка.
        s2: Вторая строка.

    Returns:
        Целое число — расстояние Левенштейна между s1 и s2.
    """
    if not isinstance(s1, str) or not isinstance(s2, str):
        raise TypeError("Аргументы s1 и s2 должны быть строками")

    len1, len2 = len(s1), len(s2)

    if len1 == 0:
        return len2
    if len2 == 0:
        return len1

    previous_row = list(range(len2 + 1))

    for i in range(1, len1 + 1):
        current_row = [i] + [0] * len2
        char1 = s1[i - 1]
        for j in range(1, len2 + 1):
            char2 = s2[j - 1]
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            replace_cost = previous_row[j - 1] + (char1 != char2)
            current_row[j] = min(insert_cost, delete_cost, replace_cost)
        previous_row = current_row

    return previous_row[len2]
