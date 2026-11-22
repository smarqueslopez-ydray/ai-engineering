"""Configuración centralizada de la aplicación.

Carga las variables de entorno (y el archivo .env) en un objeto tipado con
Pydantic. Si una variable tiene un tipo incorrecto, la aplicación falla al
arrancar (fail fast) en lugar de fallar en la primera petición.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno del proyecto, con su tipo y valor por defecto.

    Cada atributo se busca en las variables de entorno con el mismo nombre
    y, si no está, en el archivo .env. Las variables del .env que no estén
    declaradas aquí provocan un error de validación.

    Attributes:
        OPENAI_API_KEY: API key de OpenAI. Opcional: solo es necesaria si
            LLM_PROVIDER es "openai".
        ANTHROPIC_API_KEY: API key de Anthropic. Opcional: solo es necesaria
            si LLM_PROVIDER es "anthropic".
        LLM_PROVIDER: Proveedor de LLM a utilizar: "openai" o "anthropic".
        LLM_MODEL: Identificador del modelo que se envía al SDK del proveedor.
        APP_ENV: Entorno de ejecución (development, production...).
        LOG_LEVEL: Nivel de logging (DEBUG, INFO, WARNING, ERROR).
    """

    # Ruta relativa a la carpeta desde la que se arranca la app (estimador-cag/).
    model_config = SettingsConfigDict(env_file=".env")

    # --- Credenciales de los proveedores de LLM ---------------------------
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # --- Proveedor y modelo -----------------------------------------------
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"

    # --- Aplicación ---------------------------------------------------------
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración de la aplicación, cacheada.

    Gracias a @lru_cache, el .env se lee una sola vez: la primera llamada crea
    la instancia de Settings y las siguientes devuelven esa misma instancia
    (equivalente a un singleton). Por eso, si cambias el .env, hay que
    reiniciar el servidor para que se apliquen los cambios.

    Returns:
        La instancia única de Settings cargada del entorno y del .env.
    """
    return Settings()
