from .custom_error import CustomError
from .error_msg import ErrorMessage


class BadRequestError(CustomError):
    """Bad Request Error."""

    def __init__(self, message: str) -> None:
        """Initialize BadRequestError with a message and a status code of 400.

        Args:
            message (str): The error message.
        """
        super().__init__(message, 400)

    def serialize_error(self) -> list[ErrorMessage]:
        """Serialize the error into a list of ErrorMessage.

        Returns:
            list[ErrorMessage]: A list containing the serialized error message.
        """
        return [ErrorMessage(message=self.message)]
