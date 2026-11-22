# Estimador CAG

Servicio **FastAPI** que recibe la **transcripción de una reunión con un cliente** y devuelve una **estimación de un proyecto de software** generada por un LLM.

Usa arquitectura **CAG (Cache Augmented Generation)**: unos pocos ejemplos de estimaciones previas se inyectan directamente en el prompt de cada llamada. No hay base de datos, ni *retrieval*, ni persistencia.

> Proyecto 1 del Máster AI Engineering (LIDR), Sesión 2: *Scaffolding del proyecto FastAPI*. Este README crece con cada paso del ejercicio.

## Estado

| Paso | Qué | Estado |
|---|---|---|
| 1 | Proyecto con `uv`, dependencias y estructura de carpetas | ✅ |
| 2 | Configuración con variables de entorno (`config.py`, `.env.example`) | ✅ |
| 3 | Contexto estático: ejemplos de estimaciones previas | ⏳ |
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
