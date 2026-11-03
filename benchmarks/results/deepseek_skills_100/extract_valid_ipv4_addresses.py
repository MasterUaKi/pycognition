import re

_OCTET = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
_IPV4_PATTERN = re.compile(
    r'(?<![0-9.])'
    r'(' + _OCTET + r'\.' + _OCTET + r'\.' + _OCTET + r'\.' + _OCTET + r')'
    r'(?![0-9.])'
)


def extract_valid_ipv4_addresses(log_message: str) -> list[str]:
    """Extract all valid IPv4 addresses from a log message.

    Uses a strict regex that validates each octet is in 0-255 and
    forbids leading zeros (except the single digit '0').
    """
    if not isinstance(log_message, str):
        raise TypeError('log_message must be a str')
    return _IPV4_PATTERN.findall(log_message)
