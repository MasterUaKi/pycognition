import pytest
from extract_ipv4 import extract_ipv4


def test_simple_address():
    assert extract_ipv4('Server at 192.168.1.1 is up') == ['192.168.1.1']


def test_multiple_addresses():
    text = '10.0.0.1 and 8.8.8.8 and 255.255.255.255'
    assert extract_ipv4(text) == ['10.0.0.1', '8.8.8.8', '255.255.255.255']


def test_no_addresses():
    assert extract_ipv4('no addresses here') == []


def test_empty_string():
    assert extract_ipv4('') == []


def test_invalid_octet_too_large():
    assert extract_ipv4('256.1.1.1') == []


def test_invalid_octet_leading_zero():
    assert extract_ipv4('01.2.3.4') == []


def test_boundary_values():
    assert extract_ipv4('0.0.0.0 255.255.255.255') == ['0.0.0.0', '255.255.255.255']


def test_not_part_of_longer_number():
    assert extract_ipv4('1234.5.6.7 and 1.2.3.4.5') == []


def test_embedded_in_text():
    assert extract_ipv4('ip=172.16.254.1;') == ['172.16.254.1']


def test_type_error_on_non_str():
    with pytest.raises(TypeError):
        extract_ipv4(123)


def test_returns_list():
    result = extract_ipv4('1.2.3.4')
    assert isinstance(result, list)
