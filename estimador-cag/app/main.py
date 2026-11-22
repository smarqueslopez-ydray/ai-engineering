"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI

from app.routers import estimations

app = FastAPI(
    title="Estimador CAG",
    description="Estimación de proyectos de software a partir de transcripciones de reuniones, con arquitectura CAG",
    version="0.1.0",
)

app.include_router(estimations.router, prefix="/api/v1")


@app.get("/health")
async def get_health() -> dict[str, str]:
    """Comprueba que el servicio está en marcha (health check).

    No llama al LLM: sirve para que Docker, un balanceador o un monitor
    verifiquen que la API responde, sin coste.

    Returns:
        El estado del servicio: {"status": "healthy"}.
    """
    return {"status": "healthy"}
