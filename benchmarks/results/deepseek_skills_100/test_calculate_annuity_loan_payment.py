import math
import pytest
from calculate_annuity_loan_payment import calculate_annuity_loan_payment


def test_zero_interest():
    result = calculate_annuity_loan_payment(1200.0, 0.0, 12)
    assert result['monthly_payment'] == pytest.approx(100.0)
    assert result['total_interest'] == pytest.approx(0.0)


def test_standard_case():
    # 100000 at 12% annual for 12 months
    result = calculate_annuity_loan_payment(100000.0, 12.0, 12)
    monthly_rate = 0.12 / 12.0
    factor = (1.0 + monthly_rate) ** 12
    expected_payment = 100000.0 * monthly_rate * factor / (factor - 1.0)
    expected_interest = expected_payment * 12 - 100000.0
    assert result['monthly_payment'] == pytest.approx(expected_payment)
    assert result['total_interest'] == pytest.approx(expected_interest)


def test_long_tenure():
    result = calculate_annuity_loan_payment(500000.0, 6.5, 360)
    assert result['monthly_payment'] > 0
    assert result['total_interest'] > 0
    assert result['monthly_payment'] * 360 == pytest.approx(500000.0 + result['total_interest'])


def test_integer_inputs():
    result = calculate_annuity_loan_payment(1000, 10, 10)
    assert isinstance(result['monthly_payment'], float)
    assert isinstance(result['total_interest'], float)


def test_negative_principal():
    with pytest.raises(ValueError):
        calculate_annuity_loan_payment(-1000.0, 5.0, 12)


def test_zero_principal():
    with pytest.raises(ValueError):
        calculate_annuity_loan_payment(0.0, 5.0, 12)


def test_negative_rate():
    with pytest.raises(ValueError):
        calculate_annuity_loan_payment(1000.0, -1.0, 12)


def test_zero_tenure():
    with pytest.raises(ValueError):
        calculate_annuity_loan_payment(1000.0, 5.0, 0)


def test_negative_tenure():
    with pytest.raises(ValueError):
        calculate_annuity_loan_payment(1000.0, 5.0, -12)


def test_wrong_type_principal():
    with pytest.raises(TypeError):
        calculate_annuity_loan_payment('1000', 5.0, 12)


def test_wrong_type_rate():
    with pytest.raises(TypeError):
        calculate_annuity_loan_payment(1000.0, '5', 12)


def test_wrong_type_tenure():
    with pytest.raises(TypeError):
        calculate_annuity_loan_payment(1000.0, 5.0, 12.0)


def test_bool_rejected():
    with pytest.raises(TypeError):
        calculate_annuity_loan_payment(True, 5.0, 12)
