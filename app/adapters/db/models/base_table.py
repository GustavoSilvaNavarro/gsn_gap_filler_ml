from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """Base field for all the tables."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)

    def as_dict(self) -> dict:
        """Return the model as a dictionary.

        Returns:
            dict: A dictionary representation of the model.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self) -> str:
        """Provide a detailed string representation including all columns.

        Returns:
            str: A string representation of the model.
        """
        column_representations = [f"{column.name}={getattr(self, column.name)!r}" for column in self.__table__.columns]

        return f"{self.__class__.__name__}({', '.join(column_representations)})"
