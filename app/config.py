from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Main setup for the backend service."""

    # APP SETTINGS
    ENVIRONMENT: str = Field(description="Environment type", default="local")
    PORT: int = Field(description="Server Port", default=8080)
    URL_PREFIX: str = Field(description="URL to prefix routes on server", default="api")

    # ENTRY POINTS
    API_URL: str = Field(description="Server API url", default="http://localhost:8080")

    # ADAPTERS
    SERVICE_NAME: str = Field(description="Service name for the server", default="gap_filler")
    LOG_LEVEL: str = Field(
        description="Python logging level. Must be a string like 'DEBUG' or 'ERROR'.",
        default="INFO",
    )

    class Config:
        """Override env file, used in dev."""

        env_file = ".env"


config = Config()
