from fastapi import FastAPI

from app.adapters import logger
from app.config import config

from .routes import router


def start_server(server: FastAPI) -> FastAPI:
    """Run server and attach all the endpoints.

    Returns:
        FastAPI: The FastAPI server instance with routes attached.
    """
    server.include_router(
        router=router,
        prefix=f"/{config.URL_PREFIX}" if config.ENVIRONMENT not in {"local", "test"} else "",
    )

    logger.info("🎃 Server is starting...")
    return server
