# Import pytest for test functions, parametrization, and exception assertions.
import pytest

# Import the network service module under a short alias.
from services import network as svc


# Verify that a correctly formatted IPv4 address is accepted.
def test_valid_ipv4():
    # Confirm that the service recognizes a valid IPv4 address.
    assert svc.is_valid_ipv4("192.168.1.10")


# Run the same invalid IPv4 test for several invalid values.
@pytest.mark.parametrize("bad", ["256.1.1.1", "192.168.1", "abc", "::1", ""])
def test_invalid_ipv4(bad):
    # Confirm that the service rejects the invalid address.
    assert not svc.is_valid_ipv4(bad)


# Verify the calculated values for a standard /24 subnet.
def test_subnet_24():
    # Calculate subnet details from a CIDR network.
    info = svc.calculate_subnet("192.168.1.0/24")
    # Check the network address.
    assert info.network_address == "192.168.1.0"
    # Check the broadcast address.
    assert info.broadcast_address == "192.168.1.255"
    # Check the subnet netmask.
    assert info.netmask == "255.255.255.0"
    # Check the total number of addresses.
    assert info.total_addresses == 256
    # Check the number of usable host addresses.
    assert info.usable_hosts == 254
    # Check the first usable host address.
    assert info.first_host == "192.168.1.1"
    # Check the last usable host address.
    assert info.last_host == "192.168.1.254"


# Verify that host bits are normalized for a non-strict subnet.
def test_subnet_non_strict():
    # Confirm that an address inside the subnet resolves to the network address.
    assert svc.calculate_subnet("192.168.1.77/24").network_address == "192.168.1.0"


# Verify the usable host count for a /30 subnet.
def test_subnet_30():
    # Confirm that a /30 subnet provides two usable host addresses.
    assert svc.calculate_subnet("10.0.0.0/30").usable_hosts == 2


# Verify that an invalid CIDR raises the expected exception.
def test_subnet_invalid():
    # Expect the service to raise ValueError for malformed CIDR input.
    with pytest.raises(ValueError):
        # Call the service with an invalid CIDR value.
        svc.calculate_subnet("pas-un-cidr")


# Verify that allowed domains and addresses pass the target allowlist.
def test_allowed_targets():
    # Confirm that the configured base domain is allowed.
    assert svc.is_target_allowed("example.com")
    # Confirm that subdomains of an allowed domain are allowed.
    assert svc.is_target_allowed("www.example.com")
    # Confirm that an address inside the allowed private network is allowed.
    assert svc.is_target_allowed("192.168.56.20")
    # Confirm that an address outside the allowlist is rejected.
    assert not svc.is_target_allowed("8.8.8.8")
