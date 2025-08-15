from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """Basic error message object."""

    message: str
    field: str | None = None
