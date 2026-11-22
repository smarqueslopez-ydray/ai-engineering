"""Schemas de request y response del endpoint de estimación."""

from pydantic import BaseModel, Field


class EstimationRequest(BaseModel):
    """Cuerpo de la petición de estimación.

    Attributes:
        transcription: Transcripción de la reunión con el cliente. Mínimo 50
            caracteres, para no llamar al LLM con un texto vacío o sin
            información suficiente.
    """

    transcription: str = Field(
        ...,
        min_length=50,
        description="Transcripción de la reunión con el cliente",
    )


class Usage(BaseModel):
    """Tokens consumidos en la llamada al LLM.

    Attributes:
        input_tokens: Tokens de entrada (system prompt y transcripción).
        output_tokens: Tokens de salida (la estimación generada).
    """

    input_tokens: int
    output_tokens: int


class EstimationResponse(BaseModel):
    """Respuesta del endpoint de estimación.

    Attributes:
        estimation: Estimación generada por el LLM, en Markdown.
        model: Modelo exacto que generó la estimación (snapshot).
        provider: Proveedor de LLM utilizado.
        usage: Tokens consumidos en la llamada.
    """

    estimation: str
    model: str
    provider: str
    usage: Usage
