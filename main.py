# Point d'entrée de l'application FastAPI
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

# Importe les deux modules de routes (endpoints REST)
from routers import diagnostics, network

# Dossier du front-end, calculé depuis l'emplacement de ce fichier
STATIC_DIR = Path(__file__).parent / "static"

# Crée l'application ; ces informations apparaissent dans /docs
app = FastAPI(
    title="NetAutomate",
    description="API de diagnostic et de développement réseau (usage autorisé uniquement).",
    version="1.0.0",
)

# Enregistre les routes : /api/interfaces, /api/subnet, /api/diagnostics/...
app.include_router(network.router)
app.include_router(diagnostics.router)


# Endpoint de santé, utilisé par le HEALTHCHECK Docker
@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


# Page d'accueil : sert le front-end (masquée dans /docs)
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
