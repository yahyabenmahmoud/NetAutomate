# Import types used to describe lists and optional values.
from typing import List, Optional

# Import Pydantic tools used to define and validate schemas.
from pydantic import BaseModel, Field


# Describe the details reported for a network interface.
class InterfaceInfo(BaseModel):
    # Store the interface name.
    name: str
    # Indicate whether the interface is currently active.
    is_up: bool
    # Store the link speed and prevent negative values.
    speed_mbps: int = Field(ge=0)
    # Store the MTU and prevent negative values.
    mtu: int = Field(ge=0)
    # Store the interface's IPv4 addresses.
    ipv4: List[str]
    # Store the interface's IPv6 addresses.
    ipv6: List[str]
    # Store the MAC address when one is available.
    mac: Optional[str] = None


# Describe the main network settings for a device.
class NetworkConfig(BaseModel):
    # Store the device hostname.
    hostname: str
    # Store the fully qualified domain name.
    fqdn: str
    # Store the default gateway when one is configured.
    default_gateway: Optional[str] = None
    # Store the DNS servers used by the device.
    dns_servers: List[str]


# Describe the addresses resolved for a hostname.
class DnsResult(BaseModel):
    # Store the hostname that was queried.
    hostname: str
    # Store the addresses returned by DNS.
    addresses: List[str]


# Describe the result of a network connectivity check.
class ConnectivityResult(BaseModel):
    # Store the host that was tested.
    host: str
    # Store the tested port and require a valid TCP/UDP port range.
    port: int = Field(ge=1, le=65535)
    # Indicate whether the host and port were reachable.
    reachable: bool
    # Store the response latency when it was measured.
    latency_ms: Optional[float] = Field(default=None, ge=0)
    # Store an error message when the connectivity check failed.
    error: Optional[str] = None


# Describe the calculated details of an IP subnet.
class SubnetInfo(BaseModel):
    # Store the subnet in CIDR notation.
    cidr: str
    # Store the first address that identifies the network.
    network_address: str
    # Store the address used to broadcast to the subnet.
    broadcast_address: str
    # Store the subnet's netmask.
    netmask: str
    # Store the wildcard mask.
    wildcard: str
    # Store the CIDR prefix length and keep it within IPv4/IPv6 limits.
    prefix_length: int = Field(ge=0, le=128)
    # Store the total number of addresses in the subnet.
    total_addresses: int = Field(ge=0)
    # Store the number of addresses available for hosts.
    usable_hosts: int = Field(ge=0)
    # Store the first usable host address when one exists.
    first_host: Optional[str] = None
    # Store the last usable host address when one exists.
    last_host: Optional[str] = None


# Describe a network device discovered by the application.
class Device(BaseModel):
    # Store the device identifier.
    id: int = Field(ge=0)
    # Store the device name.
    name: str
    # Store the device type.
    type: str
    # Store the device IP address.
    ip: str
    # Store where the device is located.
    location: str
    # Store the device's current status.
    status: str