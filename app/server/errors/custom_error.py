from abc import ABC, abstractmethod

from .error_msg import ErrorMessage


class CustomError(Exception, ABC):
    """Custom errors."""

    message: str
    status_code: int

    def __init__(self, message: str, status_code: int) -> None:
        """Initialize CustomError with a message and status code.

        Args:
            message (str): The error message.
            status_code (int): The HTTP status code associated with the error.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @abstractmethod
    def serialize_error(self) -> list[ErrorMessage]:
        """Serialize different type of errors."""
        error_message = "Implement method"
        raise NotImplementedError(error_message)
