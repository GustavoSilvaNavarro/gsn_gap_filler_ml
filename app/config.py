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

    # DB
    LOGS_DB: bool = Field(description="Display logs sqlalchemy", default=False)
    DB_URL: str = Field(description="DB URL for the backend", default="")
    DB_USERNAME: str = Field(description="DB Username", default="postgres")
    DB_HOST: str = Field(description="DB Host", default="127.0.0.1")
    DB_PORT: int = Field(description="DB Port", default=5433)
    DB_PASSWORD: str = Field(description="DB Password", default="")
    DB_NAME: str = Field(description="DB Name", default="")

    def _get_db_url(self) -> str:
        db_username = self.DB_USERNAME
        db_password = self.DB_PASSWORD
        db_name = self.DB_NAME
        db_host = self.DB_HOST
        db_port = self.DB_PORT

        return f"postgresql+asyncpg://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

    @property
    def retrieve_db_url(self) -> str:
        """Return db url for the connection to db."""
        if self.DB_URL:
            return self.DB_URL

        return self._get_db_url()

    class Config:
        """Override env file, used in dev."""

        env_file = ".env"


config = Config()
