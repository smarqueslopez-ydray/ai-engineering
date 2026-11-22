"""Endpoints de estimación: reciben la transcripción y devuelven la estimación."""

from fastapi import APIRouter

from app.schemas.estimation import EstimationRequest, EstimationResponse
from app.services.llm_service import generate_estimation

router = APIRouter(tags=["estimations"])


@router.post("/estimate", response_model=EstimationResponse)
async def estimate(request: EstimationRequest) -> dict:
    """Genera una estimación de proyecto a partir de una transcripción.

    Router fino: valida la petición (Pydantic), delega en el servicio de LLM y
    devuelve el resultado, que FastAPI valida y serializa con
    EstimationResponse.

    Args:
        request: Petición con la transcripción de la reunión.

    Returns:
        Diccionario con estimation, model, provider y usage, que FastAPI
        convierte en EstimationResponse.
    """
    return await generate_estimation(request.transcription)
