# 1. IMPORTS

# List: used to specify that an API response contains multiple objects.
from typing import List

# APIRouter: creates and organizes API endpoints.
# HTTPException: returns HTTP errors to the client.
# Query: defines and validates URL query parameters.
from fastapi import APIRouter, HTTPException, Query

# Import the Pydantic schemas defining the structure of API responses.
from models.schemas import Device, InterfaceInfo, NetworkConfig, SubnetInfo

# Import the network service module.
# "svc" is an alias used to call its functions more easily.
from services import network as svc


# 2. ROUTER CONFIGURATION

# Create a router for network-related endpoints.
# prefix="/api": all routes start with /api.
# tags=["network"]: groups these endpoints in Swagger documentation.
router = APIRouter(prefix="/api", tags=["network"])


# 3. GET NETWORK INTERFACES

# HTTP GET endpoint: GET /api/interfaces
# response_model: the response must be a list of InterfaceInfo objects.
@router.get("/interfaces", response_model=List[InterfaceInfo])
def get_interfaces():

    # Call the service function that retrieves network interfaces.
    # The function returns the result to the API client.
    return svc.list_interfaces()


# 4. GET NETWORK CONFIGURATION

# HTTP GET endpoint: GET /api/network/config
# response_model: the response must follow the NetworkConfig schema.
@router.get("/network/config", response_model=NetworkConfig)
def get_config():

    # Call the service function that retrieves network configuration.
    return svc.get_network_config()


# 5. CALCULATE SUBNET INFORMATION

# HTTP GET endpoint: GET /api/subnet
# response_model: the result must follow the SubnetInfo schema.
@router.get("/subnet", response_model=SubnetInfo)
def get_subnet(

    # Define a required query parameter named "cidr".
    # Query(...): the parameter is mandatory.
    # description: explains the expected format in Swagger documentation.
    #
    # Example: /api/subnet?cidr=192.168.1.0/24
    cidr: str = Query(
        ...,
        description="Ex: 192.168.1.0/24"
    )
):

    # Try to calculate subnet information.
    try:

        # Send the CIDR value to the service layer for calculation.
        return svc.calculate_subnet(cidr)

    # Catch a ValueError if the CIDR is invalid.
    # "exc" contains the error message.
    except ValueError as exc:

        # Return HTTP 422 (Unprocessable Entity).
        # "detail" explains the reason for the error.
        raise HTTPException(
            status_code=422,
            detail="CIDR IPv4 invalide : %s" % exc
        )


# 6. GET NETWORK DEVICES

# HTTP GET endpoint: GET /api/devices
# response_model: the response is a list of Device objects.
@router.get("/devices", response_model=List[Device])
def get_devices():

    # Call the service function that retrieves the device inventory.
    return svc.list_devices()