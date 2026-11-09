#
#  Point d'entrée de l'application FastAPI
from fastapi import FastAPI

# Importe les deux modules de routes (endpoints REST)
from routers import diagnostics, network

# Crée l'application ; ces informations apparaissent dans /docs
app = FastAPI(
    title="NetAutomate",
    description="API de diagnostic et de developpement reseau (usage autorise uniquement).",
    version="1.0.0",
)

# Enregistre les routes : /api/interfaces, /api/subnet, /api/diagnostics/...
app.include_router(network.router)
app.include_router(diagnostics.router)


# Endpoint de santé, utilisé par le HEALTHCHECK Docker
@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
