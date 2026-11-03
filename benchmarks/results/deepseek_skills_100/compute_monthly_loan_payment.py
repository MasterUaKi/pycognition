def compute_monthly_loan_payment(principal: float, annual_rate: float, months: int) -> float:
    """
    Calculate the fixed monthly payment for an amortizing loan.

    Args:
        principal: Loan amount (must be > 0).
        annual_rate: Annual interest rate as a percentage (e.g., 5.0 for 5%).
        months: Loan term in months (must be a positive integer).

    Returns:
        The fixed monthly payment amount.

    Raises:
        ValueError: If principal <= 0, annual_rate < 0, or months <= 0.
        TypeError: If arguments are not of the expected types.
    """
    if not isinstance(principal, (int, float)) or isinstance(principal, bool):
        raise TypeError("principal must be a number")
    if not isinstance(annual_rate, (int, float)) or isinstance(annual_rate, bool):
        raise TypeError("annual_rate must be a number")
    if not isinstance(months, int) or isinstance(months, bool):
        raise TypeError("months must be an integer")

    if principal <= 0:
        raise ValueError("principal must be greater than 0")
    if annual_rate < 0:
        raise ValueError("annual_rate must be non-negative")
    if months <= 0:
        raise ValueError("months must be greater than 0")

    monthly_rate = annual_rate / 100.0 / 12.0

    if monthly_rate == 0:
        return principal / months

    factor = (1 + monthly_rate) ** months
    payment = principal * monthly_rate * factor / (factor - 1)
    return payment
