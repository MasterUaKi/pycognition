from datetime import date


def count_working_days(start_date: str, end_date: str) -> int:
    """Подсчитывает количество рабочих дней (исключая субботы и воскресенья)
    между двумя датами включительно.

    Аргументы:
        start_date: строка в формате 'YYYY-MM-DD' — начальная дата (включительно).
        end_date: строка в формате 'YYYY-MM-DD' — конечная дата (включительно).

    Возвращает:
        Целое число — количество рабочих дней в указанном периоде.

    Исключения:
        ValueError: если дата не соответствует формату 'YYYY-MM-DD'
                    или start_date > end_date.
    """
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError(
            f"start_date ({start_date}) не может быть позже end_date ({end_date})"
        )

    total_days = (end - start).days + 1
    full_weeks, remainder = divmod(total_days, 7)
    working_days = full_weeks * 5

    start_weekday = start.weekday()  # 0 = понедельник, 6 = воскресенье
    for offset in range(remainder):
        if (start_weekday + offset) % 7 < 5:
            working_days += 1

    return working_days
