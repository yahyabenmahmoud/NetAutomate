# ============================================================
# 1. IMPORTS
# ============================================================

# Import Python's socket module.
# It provides network-related functions and error types.
# We use socket.gaierror to handle DNS resolution errors.
import socket

# APIRouter: organizes related API endpoints.
# HTTPException: returns HTTP errors to the client.
# Query: defines and validates URL query parameters.
from fastapi import APIRouter, HTTPException, Query

# Import the Pydantic schemas used to structure API responses.
# ConnectivityResult: describes the result of a TCP connectivity test.
# DnsResult: describes the result of a DNS resolution.
from models.schemas import ConnectivityResult, DnsResult

# Import the network service module.
# "svc" is an alias that makes its functions easier to call.
from services import network as svc


# ============================================================
# 2. ROUTER CONFIGURATION
# ============================================================

# Create a router dedicated to network diagnostics.
#
# prefix="/api/diagnostics":
# All endpoints in this router start with /api/diagnostics.
#
# tags=["diagnostics"]:
# Groups these endpoints under "diagnostics" in Swagger documentation.
router = APIRouter(
    prefix="/api/diagnostics",
    tags=["diagnostics"]
)


# ============================================================
# 3. DNS RESOLUTION ENDPOINT
# ============================================================

# Define an HTTP GET endpoint:
# GET /api/diagnostics/dns
#
# response_model=DnsResult:
# FastAPI validates the returned data using the DnsResult schema.
@router.get("/dns", response_model=DnsResult)
def dns(

    # Define a required query parameter named "hostname".
    #
    # Query(...): means the parameter is mandatory.
    # min_length=1: prevents an empty hostname.
    # max_length=253: limits the hostname length.
    #
    # Example:
    # /api/diagnostics/dns?hostname=example.com
    hostname: str = Query(
        ...,
        min_length=1,
        max_length=253
    )
):

    # SECURITY CHECK:
    # Verify whether the requested hostname is an authorized target.
    #
    # is_target_allowed() is implemented in the service layer.
    # It should enforce an explicit allowlist of permitted targets.
    if not svc.is_target_allowed(hostname):

        # Reject the request if the target is not authorized.
        # HTTP 403 = Forbidden.
        raise HTTPException(
            status_code=403,
            detail="Cible non autorisee"
        )

    # Try to resolve the hostname using the DNS service.
    try:

        # Call the service function that performs DNS resolution.
        # Return its result to the API client.
        return svc.resolve_dns(hostname)

    # Catch a DNS/address resolution error.
    # socket.gaierror can occur when the hostname cannot be resolved.
    except socket.gaierror:

        # Return HTTP 404 with an explanatory error message.
        raise HTTPException(
            status_code=404,
            detail="Nom introuvable"
        )


# ============================================================
# 4. TCP CONNECTIVITY ENDPOINT
# ============================================================

# Define an HTTP GET endpoint:
# GET /api/diagnostics/connectivity
#
# response_model=ConnectivityResult:
# The returned data must follow the ConnectivityResult schema.
@router.get("/connectivity", response_model=ConnectivityResult)
def connectivity(

    # Required query parameter representing the destination hostname or IP.
    #
    # min_length=1: the value cannot be empty.
    # max_length=253: limits the input length.
    #
    # Example: host=example.com
    host: str = Query(
        ...,
        min_length=1,
        max_length=253
    ),

    # Required query parameter representing the TCP port.
    #
    # ge=1: minimum permitted value is 1.
    # le=65535: maximum permitted value is 65535.
    #
    # Example: port=443
    port: int = Query(
        ...,
        ge=1,
        le=65535
    )
):

    # SECURITY CHECK:
    # Verify whether the requested destination is authorized.
    if not svc.is_target_allowed(host):

        # Reject the request if the destination is not authorized.
        # HTTP 403 = Forbidden.
        raise HTTPException(
            status_code=403,
            detail="Cible non autorisee"
        )

    # Call the service function to test TCP connectivity.
    #
    # host: destination hostname or IP address.
    # port: destination TCP port.
    #
    # Return the connectivity result to the API client.
    return svc.check_connectivity(host, port)