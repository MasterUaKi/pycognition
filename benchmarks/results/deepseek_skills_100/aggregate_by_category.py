def aggregate_by_category(records):
    """Aggregate transaction amounts by category.

    Args:
        records: list of dicts, each with keys 'category' (string) and 'amount' (number).

    Returns:
        dict mapping category (string) to total amount (number).
    """
    totals = {}
    for record in records:
        category = record['category']
        amount = record['amount']
        if category in totals:
            totals[category] += amount
        else:
            totals[category] = amount
    return totals
