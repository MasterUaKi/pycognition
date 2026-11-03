from datetime import date, timedelta


def count_business_days(start_date: str, end_date: str) -> int:
    """
    Подсчитывает количество рабочих дней (понедельник–пятница)
    в полуоткрытом интервале [start_date, end_date).

    Аргументы:
        start_date: ISO 8601 дата начала (включительно), например '2026-12-15'.
        end_date:   ISO 8601 дата окончания (не включая), например '2027-01-15'.

    Возвращает:
        int — количество рабочих дней.
    """
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start >= end:
        return 0

    total_days = (end - start).days
    full_weeks, remainder = divmod(total_days, 7)
    business_days = full_weeks * 5

    start_weekday = start.weekday()  # 0 = понедельник, 6 = воскресенье
    for i in range(remainder):
        if (start_weekday + i) % 7 < 5:
            business_days += 1

    return business_days
