"""Servicio de llamada al LLM: construye el prompt con el contexto CAG y llama al modelo.

Flujo de una estimación:
    1. format_examples() convierte las estimaciones de referencia en texto.
    2. build_system_prompt() las inyecta en el system prompt, junto con las
       instrucciones, las reglas y el formato de salida (arquitectura CAG).
    3. generate_estimation() envía el system prompt y la transcripción al LLM y
       devuelve la estimación con sus metadatos.

De momento solo se usa OpenAI (Chat Completions). El SDK de Anthropic está
instalado para añadirlo como segundo proveedor en la Sesión 3 (wrappers).
"""

from openai import OpenAI

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES, HOURLY_RATES

# --- Cliente y configuración --------------------------------------------------
# Se crean una sola vez, al cargar el módulo, y se reutilizan en cada petición.
# La API key sale de la configuración (.env), nunca del código.
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# --- Contexto CAG -------------------------------------------------------------
def format_examples(examples: list[dict[str, str]]) -> str:
    """Convierte las estimaciones de referencia en texto para el prompt.

    Args:
        examples: Estimaciones de referencia, cada una con las claves
            "meeting_summary" y "estimation".

    Returns:
        Las estimaciones separadas por delimitadores numerados.
    """
    parts = []
    for number, example in enumerate(examples, start=1):
        parts.append(f"===== ESTIMACIÓN DE REFERENCIA {number} =====")
        parts.append(f"Resumen de la reunión: {example['meeting_summary']}")
        parts.append(example["estimation"])
    parts.append("===== FIN DE ESTIMACIONES DE REFERENCIA =====")
    return "\n".join(parts)


# --- System prompt ------------------------------------------------------------
def build_system_prompt() -> str:
    """Construye el system prompt con las instrucciones y el contexto CAG.

    Sigue el orden recomendado para evitar el efecto "lost in the middle":
    instrucciones al principio, estimaciones de referencia en medio y reglas
    y formato de salida cerca del final. La transcripción no va aquí: se envía
    después, como mensaje del usuario.

    Returns:
        El system prompt completo, listo para enviar al modelo.
    """
    examples_text = format_examples(ESTIMATION_EXAMPLES)
    rates_text = "\n".join(
        f"  - {profile}: {rate} €/h" for profile, rate in HOURLY_RATES.items()
    )

    # Cada parte se escribe pegada al margen izquierdo para que la sangría del
    # código no se envíe al modelo.
    return f"""\
Eres un consultor senior de estimación de proyectos de software, con más de 15
años de experiencia en una empresa de desarrollo a medida.

Tu tarea es analizar la transcripción de una reunión con un cliente y generar
una estimación detallada del proyecto: tareas, perfiles, horas, costes, equipo y
duración.

A continuación tienes estimaciones de proyectos anteriores de la empresa. Úsalas
como referencia para calibrar las tarifas, el nivel de detalle del desglose, la
proporción de testing y gestión, y el formato. No copies ningún ejemplo: adapta
las tareas al proyecto concreto de la transcripción.

{examples_text}

## Reglas de la estimación
- Usa solo estos perfiles y tarifas:
{rates_text}
- Coste de cada tarea = horas x tarifa del perfil.
- Incluye "Testing y QA" (15 % de las horas de desarrollo: frontend, backend y
  móvil) y "Gestión del proyecto" (10 % del total de horas).
- Redondea las horas a múltiplos de 5. Moneda: EUR.
- Si a la transcripción le falta información, no la inventes: indícalo como
  supuesto.

## Formato de la respuesta
Responde en español y en Markdown, con la misma estructura que las
estimaciones de referencia:
1. Título: "## Estimación: <nombre del proyecto>".
2. "### Desglose de tareas", con la tabla | Tarea | Perfil | Horas | Tarifa | Coste |.
3. "**Total estimado: <horas> horas · <coste> €**".
4. "**Equipo recomendado:**" y "**Duración estimada:**".
5. "### Supuestos y riesgos": lo que has asumido por falta de información."""


# --- Llamada al LLM ------------------------------------------------------------
async def generate_estimation(transcription: str) -> dict:
    """Genera la estimación de un proyecto a partir de una transcripción.

    Envía al modelo el system prompt (instrucciones y estimaciones de
    referencia) y la transcripción como mensaje del usuario.

    Args:
        transcription: Transcripción de la reunión con el cliente.

    Returns:
        Diccionario con las claves:
            - estimation: estimación generada, en Markdown.
            - model: modelo exacto que respondió (snapshot).
            - provider: proveedor de LLM utilizado.
            - usage: tokens de entrada (input_tokens) y de salida
              (output_tokens).

    Raises:
        openai.APIError: Si la llamada a OpenAI falla. Casos típicos: API key
            inválida o caducada (401), límite de peticiones o de crédito
            superado (429) o modelo inexistente (404). De momento no se
            gestionan aquí: se propagan a quien llama.

    Note:
        Sigue el ejemplo de la lectura 3: función async con el cliente
        síncrono OpenAI, así que la llamada bloquea el servidor mientras espera
        al modelo. Mejora pendiente: usar AsyncOpenAI y `await`.
    """
    system_prompt = build_system_prompt()

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        # Límite de salida. La lectura 5 recomienda 2.000-4.000 tokens para
        # estimaciones: si es demasiado bajo, la respuesta se corta.
        max_tokens=3000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription},
        ],
    )

    return {
        "estimation": response.choices[0].message.content,
        "model": response.model,
        "provider": settings.LLM_PROVIDER,
        "usage": {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        },
    }
