import pytest
from compute_monthly_loan_payment import compute_monthly_loan_payment


def test_zero_interest():
    assert compute_monthly_loan_payment(1200.0, 0.0, 12) == pytest.approx(100.0)


def test_standard_loan():
    # $100,000 at 6% annual for 360 months (30 years)
    payment = compute_monthly_loan_payment(100000.0, 6.0, 360)
    assert payment == pytest.approx(599.55, rel=1e-4)


def test_short_term_high_rate():
    payment = compute_monthly_loan_payment(1000.0, 12.0, 12)
    assert payment == pytest.approx(88.85, rel=1e-4)


def test_principal_equals_payment_when_one_month():
    payment = compute_monthly_loan_payment(500.0, 5.0, 1)
    assert payment == pytest.approx(500.0 * (1 + 0.05 / 12))


def test_invalid_principal_zero():
    with pytest.raises(ValueError):
        compute_monthly_loan_payment(0.0, 5.0, 12)


def test_invalid_principal_negative():
    with pytest.raises(ValueError):
        compute_monthly_loan_payment(-100.0, 5.0, 12)


def test_invalid_annual_rate_negative():
    with pytest.raises(ValueError):
        compute_monthly_loan_payment(1000.0, -1.0, 12)


def test_invalid_months_zero():
    with pytest.raises(ValueError):
        compute_monthly_loan_payment(1000.0, 5.0, 0)


def test_invalid_months_negative():
    with pytest.raises(ValueError):
        compute_monthly_loan_payment(1000.0, 5.0, -12)


def test_type_error_principal():
    with pytest.raises(TypeError):
        compute_monthly_loan_payment("1000", 5.0, 12)


def test_type_error_annual_rate():
    with pytest.raises(TypeError):
        compute_monthly_loan_payment(1000.0, "5", 12)


def test_type_error_months():
    with pytest.raises(TypeError):
        compute_monthly_loan_payment(1000.0, 5.0, 12.0)


def test_type_error_months_bool():
    with pytest.raises(TypeError):
        compute_monthly_loan_payment(1000.0, 5.0, True)
