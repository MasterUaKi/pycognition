import pytest

from extract_valid_ipv4_addresses import extract_valid_ipv4_addresses


def test_empty_string():
    assert extract_valid_ipv4_addresses('') == []


def test_no_ip():
    assert extract_valid_ipv4_addresses('no addresses here') == []


def test_simple_ip():
    assert extract_valid_ipv4_addresses('client 192.168.1.1 connected') == ['192.168.1.1']


def test_multiple_ips_in_order():
    msg = 'from 10.0.0.1 to 172.16.254.3 and 8.8.8.8'
    assert extract_valid_ipv4_addresses(msg) == ['10.0.0.1', '172.16.254.3', '8.8.8.8']


def test_boundary_octets():
    assert extract_valid_ipv4_addresses('0.0.0.0 255.255.255.255') == ['0.0.0.0', '255.255.255.255']


def test_out_of_range_octet():
    assert extract_valid_ipv4_addresses('256.1.1.1') == []
    assert extract_valid_ipv4_addresses('1.1.1.300') == []


def test_leading_zeros_rejected():
    assert extract_valid_ipv4_addresses('01.2.3.4') == []
    assert extract_valid_ipv4_addresses('1.02.3.4') == []
    assert extract_valid_ipv4_addresses('1.2.3.04') == []


def test_single_zero_octet_allowed():
    assert extract_valid_ipv4_addresses('0.1.2.3') == ['0.1.2.3']


def test_embedded_in_longer_number_rejected():
    assert extract_valid_ipv4_addresses('1234.1.1.1') == []
    assert extract_valid_ipv4_addresses('1.1.1.1234') == []


def test_adjacent_dots_rejected():
    assert extract_valid_ipv4_addresses('1.1.1.1.1') == []


def test_duplicates_preserved():
    assert extract_valid_ipv4_addresses('1.1.1.1 and 1.1.1.1') == ['1.1.1.1', '1.1.1.1']


def test_type_error_on_non_str():
    with pytest.raises(TypeError):
        extract_valid_ipv4_addresses(None)
    with pytest.raises(TypeError):
        extract_valid_ipv4_addresses(123)


def test_mixed_valid_and_invalid():
    msg = 'bad 999.1.1.1 good 192.168.0.1 bad 1.1.1.01'
    assert extract_valid_ipv4_addresses(msg) == ['192.168.0.1']
