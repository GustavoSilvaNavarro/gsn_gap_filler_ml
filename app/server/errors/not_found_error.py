from .custom_error import CustomError
from .error_msg import ErrorMessage


class NotFoundError(CustomError):
    """Not Found error."""

    def __init__(self, message: str) -> None:
        """Initialize NotFoundError with a message.

        Args:
            message (str): The error message.
        """
        super().__init__(message, 404)

    def serialize_error(self) -> list[ErrorMessage]:
        """Serialize the error into a list of ErrorMessage.

        Returns:
            list[ErrorMessage]: A list containing the serialized error message.
        """
        return [ErrorMessage(message=self.message)]
