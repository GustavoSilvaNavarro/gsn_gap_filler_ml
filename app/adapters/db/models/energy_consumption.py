from datetime import datetime

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base_table import BaseModel


class TimeSeriesData(BaseModel):
    """Timeseries table."""

    __tablename__ = "energy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    energy: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
