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
| 4 | Servicio de llamada al LLM | ✅ |
| 5 | Endpoint `POST /api/v1/estimate` | ✅ |
| 6 | Aplicación FastAPI (`/health`, Swagger) | ⏳ |
| 7 | Verificación | ⏳ |

## Puesta en marcha

### Requisitos

- Python **3.11+** (el proyecto fija 3.11 en `.python-version`)
- [uv](https://docs.astral.sh/uv/) como gestor de paquetes
- Una API key de **Anthropic** u **OpenAI**

### Instalación

Desde la carpeta `estimador-cag/`:

```bash
uv sync
```

### Configuración

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

#### Comprobar la configuración

Antes de arrancar el servidor, puedes comprobar que el `.env` se carga bien. Este comando **no muestra las keys**, solo si hay alguna:

```bash
uv run python -c "from app.config import get_settings; s = get_settings(); print(s.LLM_PROVIDER, s.LLM_MODEL, s.APP_ENV, s.LOG_LEVEL, bool(s.OPENAI_API_KEY or s.ANTHROPIC_API_KEY))"
```

Salida esperada con los valores por defecto y una key configurada:

```
openai gpt-4o-mini development DEBUG True
```

Si sale un `ValidationError`, consulta [Problemas frecuentes](#problemas-frecuentes).

## Arquitectura

```
estimador-cag/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Configuración desde variables de entorno
│   ├── routers/
│   │   └── estimations.py   # Endpoints HTTP (capa de transporte)
│   ├── schemas/
│   │   └── estimation.py    # Contratos de request y response (Pydantic)
│   ├── services/
│   │   └── llm_service.py   # Lógica de negocio: prompt + llamada al LLM
│   └── context/
│       └── examples.py      # Ejemplos de estimaciones (contexto CAG)
├── .env                     # Tus valores y keys (local, NO se sube)
├── .env.example             # Variables necesarias, con valores de ejemplo
├── .gitignore               # Excluye .env, .venv/ y __pycache__/
├── .python-version          # Versión de Python del proyecto (3.11)
├── pyproject.toml           # Metadatos, dependencias y configuración de ruff
├── uv.lock                  # Versiones exactas de las dependencias
└── README.md
```

Cada capa tiene una sola responsabilidad:

| Capa | Responsabilidad |
|---|---|
| `routers/` | Recibir la petición HTTP, validarla, delegar en el servicio y devolver la respuesta. No construye prompts ni llama al LLM |
| `schemas/` | Contratos de datos de la API: qué se recibe y qué se devuelve. Validan la entrada y documentan Swagger |
| `services/` | Construir el prompt con el contexto, llamar al proveedor y procesar la respuesta |
| `context/` | Datos de referencia que se inyectan en el prompt |
| `config.py` | Configuración tipada y validada desde el entorno |

## API

### `POST /api/v1/estimate`

Recibe la transcripción de una reunión y devuelve la estimación.

**Request**

```json
{
  "transcription": "En la reunión con el cliente se discutió la necesidad de..."
}
```

`transcription` es obligatoria y tiene un **mínimo de 50 caracteres**. Si falta o es más corta, la API responde **422** sin llamar al LLM.

**Response (200)**

```json
{
  "estimation": "## Estimación: ...

### Desglose de tareas
...",
  "model": "gpt-4o-mini-2024-07-18",
  "provider": "openai",
  "usage": { "input_tokens": 2414, "output_tokens": 323 }
}
```

| Campo | Descripción |
|---|---|
| `estimation` | Estimación en Markdown: tabla de tareas, total, equipo, duración y supuestos |
| `model` | Modelo exacto que la generó (*snapshot*) |
| `provider` | Proveedor de LLM |
| `usage` | Tokens de entrada y de salida de la llamada |

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

### Coste del contexto

Medido con una llamada real (22/11/2026, `gpt-4o-mini`) con la transcripción del enunciado:

| | Tokens | Coste |
|---|---|---|
| Entrada (system prompt con los 5 ejemplos + transcripción) | 2.414 | 0,000362 $ |
| Salida (estimación) | 323 | 0,000194 $ |
| **Total por estimación** | **2.737** | **≈ 0,00056 $** |

Casi toda la entrada es el contexto CAG, que se reenvía en cada llamada: con 1.000 estimaciones al día serían unos 2,4 millones de tokens de entrada diarios solo en contexto. Latencia observada: unos 5 s.

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

## Decisiones de diseño

### Proyecto y estructura
- **Arquitectura por capas** (`routers` → `services` → `context`): separa transporte, lógica y datos. Los routers son finos y la lógica vive en los servicios, así que se puede cambiar de proveedor o de prompt sin tocar los endpoints.
- **`context/` como punto de sustitución**: hoy son datos estáticos en código. Al pasar a RAG se sustituirá por un servicio de búsqueda semántica sin reescribir el resto.
- **uv y Python 3.11**: uv gestiona el entorno virtual y el lockfile (`uv.lock`), de modo que las versiones son reproducibles. Se fija Python 3.11 aunque haya versiones más nuevas, por compatibilidad de las dependencias.

### API
- **Schemas en su propia capa (`schemas/`)**, como en la lectura 3: el contrato de la API queda documentado en código, separado del transporte. El enunciado no exige la carpeta, pero la arquitectura por capas lo pide.
- **`min_length=50` en `transcription`**: una transcripción vacía o mínima se rechaza (422) antes de gastar una llamada al LLM.
- **`usage` en la respuesta**: el enunciado permite añadir campos; los tokens sirven para medir el coste de cada estimación.

### Configuración
- **Validación al arrancar (*fail fast*)**: Pydantic Settings comprueba tipos y variables al iniciar la aplicación, no en la primera petición.
- **Keys opcionales** (`str | None = None`): solo es necesaria la del proveedor elegido, así se puede trabajar con OpenAI o con Anthropic sin tener las dos.
- **Configuración cacheada** (`@lru_cache`): el `.env` se lee una vez y todas las partes de la app comparten la misma instancia.

### System prompt y llamada al LLM
- **System prompt con las 4 dimensiones** de un buen prompt: rol (consultor senior de estimación), tarea, cómo usar las estimaciones de referencia y formato de salida.
- **Orden contra el efecto *lost in the middle***: instrucciones al principio, ejemplos en medio y reglas y formato al final. La transcripción va después, como mensaje del usuario.
- **Tarifas generadas desde `HOURLY_RATES`**: si cambia una tarifa en `examples.py`, el prompt se actualiza solo.
- **Ejemplos separados por delimitadores** (`===== ESTIMACIÓN DE REFERENCIA N =====`), para que el modelo no los mezcle.
- **Solo OpenAI, con Chat Completions** (`gpt-4o-mini`), como el ejemplo del material del curso. El SDK de Anthropic está instalado para añadirlo como segundo proveedor en la Sesión 3.
- **`max_tokens=3000`**: límite de salida explícito, para que una estimación larga no se corte y no depender del valor por defecto del proveedor.
- **`model` devuelve el *snapshot* exacto** (p. ej. `gpt-4o-mini-2024-07-18`), no el alias: se sabe qué versión generó cada estimación.

### Contexto CAG
- **5 ejemplos de tipos distintos** (web, móvil, herramienta interna, integración y SaaS): dan variedad sin llenar el contexto. Entre 5 y 7 es el punto óptimo; ejemplos parecidos solo añaden tokens.
- **Markdown con el mismo formato que la respuesta esperada**: el modelo tiende a imitar el formato que ve en el contexto.
- **Tarifas fijas y totales precalculados**: el modelo se calibra con precios coherentes y no tiene que hacer cuentas, algo en lo que los LLM no son fiables.
- **Datos ficticios y anónimos**: no se usan nombres de clientes ni datos reales.

## Seguridad

- **Las API keys solo están en el `.env`**, que está en `.gitignore` y nunca se sube al repositorio. En el código no hay ninguna key.
- **`.env.example`** documenta las variables con **valores de ejemplo falsos** (`your-...-api-key-here`).
- Antes de cada commit se comprueba que el `.env` no está incluido.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ValidationError: ... Extra inputs are not permitted` al arrancar | El `.env` tiene una variable que no está declarada en `Settings` (`app/config.py`) | Declárala en `Settings` o bórrala del `.env` |
| La app no lee el `.env` (se usan los valores por defecto) | La ruta del `.env` es relativa a la carpeta desde la que se arranca | Ejecuta los comandos desde `estimador-cag/` |
| Los cambios en el `.env` no se aplican | La configuración está cacheada con `@lru_cache` | Reinicia el servidor; `--reload` no basta |
| `openai.AuthenticationError` (401) | API key inválida, revocada o caducada | Revisa `OPENAI_API_KEY` en el `.env` o crea una key nueva |
| `openai.RateLimitError` (429) | Límite de peticiones superado o sin crédito | Espera y reintenta, o revisa el saldo de la cuenta |
| `openai.NotFoundError` (404) | El modelo de `LLM_MODEL` no existe o no tienes acceso | Usa un modelo válido, p. ej. `gpt-4o-mini` |

## Limitaciones

- **La llamada al LLM es síncrona dentro de una función `async`**, como en el ejemplo del curso: bloquea el servidor mientras espera al modelo. La mejora es usar `AsyncOpenAI` y `await`.
- **Un solo proveedor (OpenAI).** Elegir proveedor con `LLM_PROVIDER` llegará en la Sesión 3.
- **Los errores de la API no se gestionan todavía**: se propagan a quien llama.
- **Todo el contexto viaja en cada llamada (CAG).** Con más de unos 10 ejemplos, el rendimiento baja (más coste y menos atención del modelo) y lo adecuado sería pasar a **RAG**, que recupera solo los ejemplos más relevantes para cada transcripción.

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
| `python-dotenv` | Lectura del archivo `.env`. Ya la traen `pydantic-settings` y `uvicorn[standard]`, pero se declara porque la pide el enunciado |
| `openai` | SDK de OpenAI, el proveedor que se usa |
| `anthropic` | SDK de Anthropic. Instalado, pero sin usar hasta la Sesión 3 (segundo proveedor) |

Las versiones de `pyproject.toml` son mínimas (`>=`) y `uv.lock` fija las exactas, así que `uv sync` instala siempre las mismas.
