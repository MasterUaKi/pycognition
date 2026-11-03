import pytest
from aggregate_by_category import aggregate_by_category


def test_empty_list():
    assert aggregate_by_category([]) == {}


def test_single_record():
    records = [{'category': 'food', 'amount': 10}]
    assert aggregate_by_category(records) == {'food': 10}


def test_multiple_same_category():
    records = [
        {'category': 'food', 'amount': 10},
        {'category': 'food', 'amount': 5},
        {'category': 'food', 'amount': 2.5},
    ]
    assert aggregate_by_category(records) == {'food': 17.5}


def test_multiple_categories():
    records = [
        {'category': 'food', 'amount': 10},
        {'category': 'transport', 'amount': 20},
        {'category': 'food', 'amount': 5},
        {'category': 'entertainment', 'amount': 15},
    ]
    assert aggregate_by_category(records) == {
        'food': 15,
        'transport': 20,
        'entertainment': 15,
    }


def test_negative_amounts():
    records = [
        {'category': 'refund', 'amount': -10},
        {'category': 'refund', 'amount': -5},
        {'category': 'purchase', 'amount': 20},
    ]
    assert aggregate_by_category(records) == {'refund': -15, 'purchase': 20}


def test_float_amounts():
    records = [
        {'category': 'a', 'amount': 0.1},
        {'category': 'a', 'amount': 0.2},
        {'category': 'b', 'amount': 1.5},
    ]
    result = aggregate_by_category(records)
    assert result['a'] == pytest.approx(0.3)
    assert result['b'] == 1.5


def test_zero_amounts():
    records = [
        {'category': 'zero', 'amount': 0},
        {'category': 'zero', 'amount': 0},
    ]
    assert aggregate_by_category(records) == {'zero': 0}


def test_mixed_int_float():
    records = [
        {'category': 'mix', 'amount': 1},
        {'category': 'mix', 'amount': 2.5},
    ]
    assert aggregate_by_category(records) == {'mix': 3.5}


def test_does_not_mutate_input():
    records = [
        {'category': 'x', 'amount': 1},
        {'category': 'x', 'amount': 2},
    ]
    original = [dict(r) for r in records]
    aggregate_by_category(records)
    assert records == original


def test_returns_new_dict_each_call():
    records = [{'category': 'a', 'amount': 1}]
    first = aggregate_by_category(records)
    second = aggregate_by_category(records)
    assert first == second
    assert first is not second
