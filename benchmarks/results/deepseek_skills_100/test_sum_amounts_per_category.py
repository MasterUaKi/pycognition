import pytest
from sum_amounts_per_category import sum_amounts_per_category


def test_empty_list():
    assert sum_amounts_per_category([]) == {}


def test_single_record():
    records = [{'category': 'food', 'amount': 10.5}]
    assert sum_amounts_per_category(records) == {'food': 10.5}


def test_multiple_categories():
    records = [
        {'category': 'food', 'amount': 10.0},
        {'category': 'transport', 'amount': 5.5},
        {'category': 'food', 'amount': 2.5},
    ]
    assert sum_amounts_per_category(records) == {'food': 12.5, 'transport': 5.5}


def test_negative_amounts():
    records = [
        {'category': 'refund', 'amount': -10.0},
        {'category': 'refund', 'amount': -5.0},
        {'category': 'income', 'amount': 100.0},
    ]
    assert sum_amounts_per_category(records) == {'refund': -15.0, 'income': 100.0}


def test_zero_amounts():
    records = [
        {'category': 'a', 'amount': 0.0},
        {'category': 'b', 'amount': 0.0},
        {'category': 'a', 'amount': 0.0},
    ]
    assert sum_amounts_per_category(records) == {'a': 0.0, 'b': 0.0}


def test_float_precision():
    records = [
        {'category': 'x', 'amount': 0.1},
        {'category': 'x', 'amount': 0.2},
    ]
    result = sum_amounts_per_category(records)
    assert result['x'] == pytest.approx(0.3)


def test_does_not_mutate_input():
    records = [
        {'category': 'food', 'amount': 10.0},
        {'category': 'food', 'amount': 5.0},
    ]
    original = [dict(r) for r in records]
    sum_amounts_per_category(records)
    assert records == original


def test_missing_key_raises():
    with pytest.raises(KeyError):
        sum_amounts_per_category([{'category': 'food'}])
    with pytest.raises(KeyError):
        sum_amounts_per_category([{'amount': 10.0}])
