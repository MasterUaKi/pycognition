def sum_amounts_per_category(records):
    """
    Суммирует значения поля amount по каждой уникальной категории.

    :param records: list[dict] — список записей с полями 'category' (str) и 'amount' (float)
    :return: dict[str, float] — словарь {категория: сумма amount}
    """
    totals = {}
    for record in records:
        category = record['category']
        amount = record['amount']
        totals[category] = totals.get(category, 0.0) + amount
    return totals
