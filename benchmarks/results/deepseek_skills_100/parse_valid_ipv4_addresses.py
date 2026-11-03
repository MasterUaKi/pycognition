import re


def parse_valid_ipv4_addresses(log_message: str) -> list[str]:
    """Extract all valid IPv4 addresses from a log message.

    A valid IPv4 address consists of exactly four octets separated by dots.
    Each octet must be a decimal number from 0 to 255 with no leading zeros
    (except the single digit '0'). Addresses are returned in order of
    appearance, without duplicates removed.
    """
    if not isinstance(log_message, str):
        raise TypeError("log_message must be a str")

    # Candidate pattern: four dot-separated groups of 1-3 digits.
    # Boundaries ensure we don't match inside longer digit/dot sequences.
    candidate_pattern = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])")

    results: list[str] = []
    for match in candidate_pattern.finditer(log_message):
        candidate = match.group(1)
        if _is_valid_ipv4(candidate):
            results.append(candidate)
    return results


def _is_valid_ipv4(candidate: str) -> bool:
    parts = candidate.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if len(part) > 1 and part[0] == "0":
            return False
        if int(part) > 255:
            return False
    return True
