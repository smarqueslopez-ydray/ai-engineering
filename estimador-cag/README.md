# Estimador CAG

Servicio **FastAPI** que recibe la **transcripción de una reunión con un cliente** y devuelve una **estimación de un proyecto de software** generada por un LLM.

Usa arquitectura **CAG (Cache Augmented Generation)**: unos pocos ejemplos de estimaciones previas se inyectan directamente en el prompt de cada llamada. No hay base de datos, ni *retrieval*, ni persistencia.

> Proyecto 1 del Máster AI Engineering (LIDR), Sesión 2: *Scaffolding del proyecto FastAPI*. Este README crece con cada paso del ejercicio.

## Estado

| Paso | Qué | Estado |
|---|---|---|
| 1 | Proyecto con `uv`, dependencias y estructura de carpetas | ✅ |
| 2 | Configuración con variables de entorno (`config.py`, `.env.example`) | ✅ |
| 3 | Contexto estático: ejemplos de estimaciones previas | ✅ |
| 4 | Servicio de llamada al LLM | ⏳ |
| 5 | Endpoint `POST /api/v1/estimate` | ⏳ |
| 6 | Aplicación FastAPI (`/health`, Swagger) | ⏳ |
| 7 | Verificación | ⏳ |

## Requisitos

- Python **3.11+** (el proyecto fija 3.11 en `.python-version`)
- [uv](https://docs.astral.sh/uv/) como gestor de paquetes
- Una API key de **Anthropic** u **OpenAI**

## Instalación

```bash
uv sync
```

## Configuración

1. Copia `.env.example` como `.env`, que **no se sube al repositorio**.
2. Pon la API key del proveedor que vayas a usar y ajusta el proveedor y el modelo.

| Variable | Descripción | Por defecto |
|---|---|---|
| `OPENAI_API_KEY` | API key de OpenAI | — (necesaria si `LLM_PROVIDER=openai`) |
| `ANTHROPIC_API_KEY` | API key de Anthropic | — (necesaria si `LLM_PROVIDER=anthropic`) |
| `LLM_PROVIDER` | Proveedor: `openai` o `anthropic` | `openai` |
| `LLM_MODEL` | Modelo, p. ej. `gpt-4o-mini` o `claude-haiku-4-5` | `gpt-4o-mini` |
| `APP_ENV` | Entorno de ejecución | `development` |
| `LOG_LEVEL` | Nivel de logging | `DEBUG` |

La configuración se carga con Pydantic Settings (`app/config.py`) y se lee **una sola vez**, gracias a `@lru_cache`. **Si cambias el `.env`, reinicia el servidor**, porque `--reload` no basta.

## Contexto CAG: ejemplos de referencia

El modelo recibe en cada llamada **5 estimaciones previas** (ficticias) como referencia, definidas en `app/context/examples.py`:

| # | Proyecto | Horas | Coste | Duración |
|---|---|---|---|---|
| 1 | Tienda online | 365 h | 18.650 € | 6–7 semanas |
| 2 | App móvil de reservas | 350 h | 18.275 € | 6–7 semanas |
| 3 | Herramienta interna de gestión | 180 h | 9.225 € | 4 semanas |
| 4 | Integración con CRM | 205 h | 11.025 € | 4–5 semanas |
| 5 | MVP de un SaaS | 440 h | 22.525 € | 8–10 semanas |

Todos siguen las mismas reglas:
- Tarifas: PM 50 · UX/UI 45 · Frontend 50 · Backend 55 · Móvil 55 · QA 40 · DevOps 60 €/h.
- QA = 15 % de las horas de desarrollo y gestión = 10 % del total.
- Horas en múltiplos de 5.

### Cómo añadir o modificar un ejemplo

Cada ejemplo de `ESTIMATION_EXAMPLES` es un diccionario con dos claves:

- `meeting_summary`: 2–3 frases con lo que pidió el cliente (producto, funcionalidades clave y condicionantes).
- `estimation`: la estimación en Markdown, con la misma estructura que los demás:
  - Título `## Estimación: <proyecto>`.
  - Tabla `| Tarea | Perfil | Horas | Tarifa | Coste |`.
  - Línea `**Total estimado: <horas> horas · <coste> €**`.
  - Equipo recomendado y duración estimada.

Al añadir o cambiar un ejemplo:

1. Usa solo perfiles y tarifas de `HOURLY_RATES`.
2. Coste de cada tarea = horas × tarifa.
3. Añade *Testing y QA* (15 % de las horas de desarrollo) y *Gestión del proyecto* (10 % del total), redondeados a múltiplos de 5.
4. Comprueba que los totales cuadran y actualiza la tabla de esta sección.

### Decisiones de diseño

- **5 ejemplos de tipos distintos** (web, móvil, herramienta interna, integración y SaaS): dan variedad sin llenar el contexto. Entre 5 y 7 es el punto óptimo; ejemplos parecidos solo añaden tokens.
- **Markdown con el mismo formato que la respuesta esperada**: el modelo tiende a imitar el formato que ve en el contexto.
- **Tarifas fijas y totales precalculados**: el modelo se calibra con precios coherentes y no tiene que hacer cuentas, algo en lo que los LLM no son fiables.
- **Datos ficticios y anónimos**: no se usan nombres de clientes ni datos reales.

### Limitaciones

Todos los ejemplos viajan en **cada llamada** (CAG). Con más de unos 10 ejemplos, el rendimiento baja (más coste y menos atención del modelo) y lo adecuado sería pasar a **RAG**, que recupera solo los ejemplos más relevantes para cada transcripción.

## Estructura

```
estimador-cag/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Configuración desde variables de entorno
│   ├── routers/
│   │   └── estimations.py   # Endpoints HTTP
│   ├── services/
│   │   └── llm_service.py   # Lógica de negocio: prompt + llamada al LLM
│   └── context/
│       └── examples.py      # Ejemplos de estimaciones (contexto CAG)
├── .env.example             # Variables necesarias, sin valores secretos
├── pyproject.toml
└── uv.lock
```

## Convenciones

- **Docstrings en Google style** (`Args:`, `Returns:`, `Raises:`, `Attributes:`), validados por ruff.
- **Lint y formato con [ruff](https://docs.astral.sh/ruff/)**, configurado en `pyproject.toml`:

```bash
uvx ruff check .
uvx ruff format .
```

## Dependencias

| Paquete | Para qué |
|---|---|
| `fastapi` | Framework de la API |
| `uvicorn[standard]` | Servidor ASGI |
| `pydantic-settings` | Configuración tipada desde variables de entorno |
| `python-dotenv` | Lectura del archivo `.env` |
| `anthropic`, `openai` | SDK de cada proveedor de LLM |
