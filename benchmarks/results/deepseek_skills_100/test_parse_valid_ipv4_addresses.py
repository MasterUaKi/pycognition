import pytest

from parse_valid_ipv4_addresses import parse_valid_ipv4_addresses


class TestParseValidIPv4Addresses:
    def test_empty_string(self):
        assert parse_valid_ipv4_addresses("") == []

    def test_single_valid_address(self):
        assert parse_valid_ipv4_addresses("Connection from 192.168.1.1 accepted") == [
            "192.168.1.1"
        ]

    def test_multiple_valid_addresses_in_order(self):
        log = "src=10.0.0.1 dst=172.16.254.3 via 8.8.8.8"
        assert parse_valid_ipv4_addresses(log) == [
            "10.0.0.1",
            "172.16.254.3",
            "8.8.8.8",
        ]

    def test_boundary_values(self):
        log = "0.0.0.0 and 255.255.255.255 are valid"
        assert parse_valid_ipv4_addresses(log) == [
            "0.0.0.0",
            "255.255.255.255",
        ]

    def test_octet_out_of_range(self):
        log = "bad 256.1.1.1 and 1.1.1.256 and 999.999.999.999"
        assert parse_valid_ipv4_addresses(log) == []

    def test_leading_zeros_rejected(self):
        log = "bad 01.2.3.4 and 1.02.3.4 and 1.2.03.4 and 1.2.3.04"
        assert parse_valid_ipv4_addresses(log) == []

    def test_single_zero_octet_allowed(self):
        log = "ok 0.1.2.3 and 1.0.2.3 and 1.2.0.3 and 1.2.3.0"
        assert parse_valid_ipv4_addresses(log) == [
            "0.1.2.3",
            "1.0.2.3",
            "1.2.0.3",
            "1.2.3.0",
        ]

    def test_too_few_octets(self):
        log = "bad 1.2.3 and 1.2 and 1"
        assert parse_valid_ipv4_addresses(log) == []

    def test_too_many_octets(self):
        log = "bad 1.2.3.4.5 and 1.2.3.4.5.6"
        assert parse_valid_ipv4_addresses(log) == []

    def test_embedded_in_longer_number_sequence(self):
        log = "bad 11.2.3.4.5 and 1.2.3.4444 and 1234.1.1.1"
        assert parse_valid_ipv4_addresses(log) == []

    def test_mixed_valid_and_invalid(self):
        log = (
            "valid 192.168.0.1 invalid 256.0.0.1 valid 10.10.10.10 "
            "invalid 01.1.1.1 valid 127.0.0.1"
        )
        assert parse_valid_ipv4_addresses(log) == [
            "192.168.0.1",
            "10.10.10.10",
            "127.0.0.1",
        ]

    def test_duplicates_preserved(self):
        log = "1.1.1.1 then 1.1.1.1 again"
        assert parse_valid_ipv4_addresses(log) == ["1.1.1.1", "1.1.1.1"]

    def test_addresses_adjacent_to_punctuation(self):
        log = "(10.0.0.1), [10.0.0.2]; 10.0.0.3!"
        assert parse_valid_ipv4_addresses(log) == [
            "10.0.0.1",
            "10.0.0.2",
            "10.0.0.3",
        ]

    def test_no_addresses(self):
        log = "no addresses here, just text and numbers 12345"
        assert parse_valid_ipv4_addresses(log) == []

    def test_non_string_raises_type_error(self):
        with pytest.raises(TypeError):
            parse_valid_ipv4_addresses(None)
        with pytest.raises(TypeError):
            parse_valid_ipv4_addresses(123)
        with pytest.raises(TypeError):
            parse_valid_ipv4_addresses(["1.1.1.1"])
