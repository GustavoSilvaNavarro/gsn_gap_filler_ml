from .custom_error import CustomError
from .error_msg import ErrorMessage


class InternalServerError(CustomError):
    """Internal Server Error."""

    details: str | None

    def __init__(self, message: str, status_code: int = 500, details: str | None = None) -> None:
        """Initialize InternalServerError with a message, status code, and optional details.

        Args:
            message (str): The error message.
            status_code (int, optional): The HTTP status code (default is 500).
            details (Optional[str], optional): Additional details about the error (default is None).
        """
        super().__init__(message, status_code)
        self.details = details

    def serialize_error(self) -> list[ErrorMessage]:
        """Serialize the error into a list of ErrorMessage.

        Returns:
            list[ErrorMessage]: A list containing the serialized error message and its field.
        """
        return [ErrorMessage(message=self.message, field=self.details)]
