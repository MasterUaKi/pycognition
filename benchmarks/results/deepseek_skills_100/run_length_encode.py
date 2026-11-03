def run_length_encode(input_string: str) -> str:
    """
    Кодирует строку с помощью кодирования длин серий (RLE).

    Каждая группа подряд идущих одинаковых символов заменяется на символ
    и количество его повторений.

    :param input_string: исходная строка для кодирования
    :return: строка в формате RLE
    """
    if not isinstance(input_string, str):
        raise TypeError("input_string должен быть строкой")

    if input_string == "":
        return ""

    result = []
    current_char = input_string[0]
    count = 1

    for char in input_string[1:]:
        if char == current_char:
            count += 1
        else:
            result.append(current_char + str(count))
            current_char = char
            count = 1

    result.append(current_char + str(count))
    return "".join(result)
