import re

_OCTET = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
_IPV4_RE = re.compile(r'(?<![0-9.])' + r'\.'.join([_OCTET] * 4) + r'(?![0-9.])')


def extract_ipv4(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError('text must be a str')
    return _IPV4_RE.findall(text)
