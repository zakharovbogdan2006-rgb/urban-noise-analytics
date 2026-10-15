from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    dbfs: Mapped[float] = mapped_column(Float)
    rms: Mapped[float] = mapped_column(Float)
    peak_frequency_hz: Mapped[float] = mapped_column(Float)
    low_energy: Mapped[float] = mapped_column(Float)
    mid_energy: Mapped[float] = mapped_column(Float)
    high_energy: Mapped[float] = mapped_column(Float)
    sample_rate: Mapped[int] = mapped_column(Integer)

    __table_args__ = (Index("ix_device_time", "device_id", "measured_at"),)

