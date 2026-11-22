# Estimador CAG

Servicio **FastAPI** que recibe la **transcripción de una reunión con un cliente** y devuelve una **estimación de un proyecto de software** generada por un LLM.

Usa arquitectura **CAG (Cache Augmented Generation)**: unos pocos ejemplos de estimaciones previas se inyectan directamente en el prompt de cada llamada. No hay base de datos, ni *retrieval*, ni persistencia.

> Proyecto 1 del Máster AI Engineering (LIDR), Sesión 2: *Scaffolding del proyecto FastAPI*. Este README crece con cada paso del ejercicio.

## Estado

| Paso | Qué | Estado |
|---|---|---|
| 1 | Proyecto con `uv`, dependencias y estructura de carpetas | ✅ |
| 2 | Configuración con variables de entorno (`config.py`, `.env.example`) | ⏳ |
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

## Dependencias

| Paquete | Para qué |
|---|---|
| `fastapi` | Framework de la API |
| `uvicorn[standard]` | Servidor ASGI |
| `pydantic-settings` | Configuración tipada desde variables de entorno |
| `python-dotenv` | Lectura del archivo `.env` |
| `anthropic`, `openai` | SDK de cada proveedor de LLM |
