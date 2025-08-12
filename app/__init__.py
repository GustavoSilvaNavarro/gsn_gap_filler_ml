from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.server import start_server
from app.server.errors import CustomError

from .adapters import init_loggers, logger
from .config import config


async def start_app(app=FastAPI) -> FastAPI:
    """Start FastApi Server with all its connections.

    Returns:
        FastAPI: The FastAPI application instance.
    """
    init_loggers(config.LOG_LEVEL)

    api_sever = start_server(app)

    logger.info("%s Service is starting...", config.SERVICE_NAME)
    logger.info("%s Server running on PORT %s", config.SERVICE_NAME, config.PORT)
    return api_sever


async def shutdown_app() -> None:
    """Shutdown FastAPI Server and Connections."""
    logger.info("Shutdown -> Server shutting down")


@asynccontextmanager
async def lifespan_manager(app: FastAPI):
    """Handle startup and shutdown events using a context manager."""
    await start_app(app=app)
    yield
    await shutdown_app()


app = FastAPI(lifespan=lifespan_manager)


@app.exception_handler(CustomError)
async def custom_error(_req: Request, err: CustomError) -> JSONResponse:  # noqa: RUF029
    """Handle custom errors and return a JSON response.

    Returns:
        JSONResponse: A JSON response with the error details and status code.
    """
    logger.error(err)
    return JSONResponse(status_code=err.status_code, content=jsonable_encoder(err.serialize_error()))


@app.exception_handler(Exception)
async def global_error(_req: Request, err: Exception) -> JSONResponse:  # noqa: RUF029
    """Global Error handler.

    Returns:
       JSONResponse: A JSON response with a 500 status code and error details.
    """
    logger.error(err)
    return JSONResponse(status_code=500, content={"error": "Server Error", "detail": str(err) or None})
