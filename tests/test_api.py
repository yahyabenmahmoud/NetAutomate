# Import FastAPI's client for sending requests to the application in tests.
from fastapi.testclient import TestClient

# Import the FastAPI application being tested.
from routers.main import app

# Create a reusable client connected to the application.
client = TestClient(app)


# Verify that the health endpoint reports the application as ready.
def test_health():
    # Send a request to the health endpoint and decode its JSON response.
    response = client.get("/health")
    # Confirm that the endpoint returns the expected healthy status.
    assert response.json() == {"status": "ok"}


# Verify that the interfaces endpoint returns successfully.
def test_interfaces():
    # Request the list of network interfaces.
    response = client.get("/api/interfaces")
    # Confirm the request succeeded and returned a list.
    assert response.status_code == 200 and isinstance(response.json(), list)


# Verify that the network configuration endpoint returns a hostname.
def test_network_config():
    # Request the current network configuration.
    response = client.get("/api/network/config")
    # Confirm the request succeeded and includes a hostname.
    assert response.status_code == 200 and "hostname" in response.json()


# Verify that a valid subnet query returns calculated subnet information.
def test_subnet_ok():
    # Request details for a valid /24 subnet.
    response = client.get("/api/subnet", params={"cidr": "192.168.1.0/24"})
    # Confirm success and verify the expected usable host count.
    assert response.status_code == 200 and response.json()["usable_hosts"] == 255


# Verify that an invalid subnet query is rejected.
def test_subnet_invalid():
    # Send a request with an invalid IP address in the CIDR value.
    response = client.get("/api/subnet", params={"cidr": "999.1.1.0/24"})
    # Confirm that the API returns a validation error.
    assert response.status_code == 422


# Verify that the devices endpoint returns at least one device.
def test_devices():
    # Request the available network devices and decode the JSON list.
    devices = client.get("/api/devices").json()
    # Confirm that the device inventory is not empty.
    assert len(devices) > 0


# Verify that DNS lookup for an allowed local hostname succeeds.
def test_dns_localhost():
    # Request DNS information for localhost.
    response = client.get("/api/diagnostics/dns", params={"hostname": "localhost"})
    # Confirm success and verify that at least one address was returned.
    assert response.status_code == 200 and response.json()["addresses"]


# Verify that DNS lookup for a forbidden hostname is blocked.
def test_dns_forbidden():
    # Request DNS information for a hostname outside the allowlist.
    response = client.get("/api/diagnostics/dns", params={"hostname": "evil.test"})
    # Confirm that the API denies the request.
    assert response.status_code == 403


# Verify that a closed local port returns an unsuccessful connectivity result.
def test_connectivity_closed_port():
    # Check connectivity to a local port expected to be closed.
    response = client.get(
        "/api/diagnostics/connectivity",
        params={"host": "127.0.0.1", "port": 1},
    )
    # Confirm the request succeeded and the port was not reachable.
    assert response.status_code == 200 and response.json()["reachable"] is False


# Verify that connectivity checks for forbidden hosts are blocked.
def test_connectivity_forbidden():
    # Request a connectivity check for a host outside the allowlist.
    response = client.get(
        "/api/diagnostics/connectivity",
        params={"host": "8.8.8.8", "port": 53},
    )
    # Confirm that the API denies the request.
    assert response.status_code == 403


# Verify that an out-of-range port is rejected by API validation.
def test_connectivity_invalid_port():
    # Request connectivity with a port above the valid maximum.
    response = client.get(
        "/api/diagnostics/connectivity",
        params={"host": "127.0.0.1", "port": 70000},
    )
    # Confirm that the API returns a validation error.
    assert response.status_code == 422
