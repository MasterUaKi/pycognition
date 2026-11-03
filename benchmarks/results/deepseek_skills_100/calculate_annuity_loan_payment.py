def calculate_annuity_loan_payment(principal: float, annual_rate: float, tenure_months: int) -> dict:
    """
    Calculate the monthly annuity loan payment and total interest paid.

    Args:
        principal: Loan principal amount (must be > 0).
        annual_rate: Annual interest rate in percent (e.g., 5.0 for 5%).
        tenure_months: Loan tenure in months (must be a positive integer).

    Returns:
        A dict with keys 'monthly_payment' and 'total_interest'.

    Raises:
        ValueError: If inputs are invalid.
        TypeError: If inputs have wrong types.
    """
    if not isinstance(principal, (int, float)) or isinstance(principal, bool):
        raise TypeError('principal must be a number')
    if not isinstance(annual_rate, (int, float)) or isinstance(annual_rate, bool):
        raise TypeError('annual_rate must be a number')
    if not isinstance(tenure_months, int) or isinstance(tenure_months, bool):
        raise TypeError('tenure_months must be an integer')

    principal = float(principal)
    annual_rate = float(annual_rate)

    if principal <= 0:
        raise ValueError('principal must be positive')
    if annual_rate < 0:
        raise ValueError('annual_rate must be non-negative')
    if tenure_months <= 0:
        raise ValueError('tenure_months must be positive')

    monthly_rate = annual_rate / 100.0 / 12.0

    if monthly_rate == 0.0:
        monthly_payment = principal / tenure_months
    else:
        factor = (1.0 + monthly_rate) ** tenure_months
        monthly_payment = principal * monthly_rate * factor / (factor - 1.0)

    total_paid = monthly_payment * tenure_months
    total_interest = total_paid - principal

    return {
        'monthly_payment': monthly_payment,
        'total_interest': total_interest,
    }
