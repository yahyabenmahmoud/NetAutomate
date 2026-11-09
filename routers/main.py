# ============================================================
# 1. IMPORTS
# ============================================================

# FastAPI: imports the main class used to create the API application.
from fastapi import FastAPI

# Import the routers containing our API endpoints.
#
# diagnostics: contains DNS and TCP connectivity endpoints.
# network: contains network interfaces, configuration,
# subnet calculation, and device inventory endpoints.
from routers import diagnostics, network


# ============================================================
# 2. CREATE THE FASTAPI APPLICATION
# ============================================================

# Create the main FastAPI application instance.
#
# FastAPI(...):
# Initializes the application and its configuration.
#
# title:
# The name displayed in the automatic API documentation.
#
# description:
# Explains the purpose of the API.
#
# version:
# Defines the current application version.
app = FastAPI(
    title="Network DevOps API",
    description="API de diagnostic et de developpement reseau (usage autorise uniquement).",
    version="1.0.0",
)


# ============================================================
# 3. REGISTER THE API ROUTERS
# ============================================================

# Register the network router in the main application.
#
# network.router:
# Contains endpoints such as:
# GET /api/interfaces
# GET /api/network/config
# GET /api/subnet
# GET /api/devices
#
# Without include_router(), these endpoints would not be
# registered in this FastAPI application.
app.include_router(network.router)


# Register the diagnostics router in the main application.
#
# diagnostics.router:
# Contains endpoints such as:
# GET /api/diagnostics/dns
# GET /api/diagnostics/connectivity
app.include_router(diagnostics.router)


# ============================================================
# 4. HEALTH CHECK ENDPOINT
# ============================================================

# Define a GET endpoint: GET /health
#
# tags=["system"]:
# Groups this endpoint under the "system" category in Swagger.
#
# Purpose:
# Allows us to check whether the API application is responding.
@app.get("/health", tags=["system"])
def health():

    # Return a simple JSON response indicating that the API is running.
    #
    # Expected response:
    # {
    #     "status": "ok"
    # }
    return {"status": "ok"}