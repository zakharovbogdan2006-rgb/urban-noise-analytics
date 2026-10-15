from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MeasurementIn(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    device_id: str = Field(min_length=1, max_length=100)
    measured_at: datetime
    dbfs: float = Field(ge=-160, le=10)
    rms: float = Field(ge=0)
    peak_frequency_hz: float = Field(ge=0)
    low_energy: float = Field(ge=0)
    mid_energy: float = Field(ge=0)
    high_energy: float = Field(ge=0)
    sample_rate: int = Field(ge=8000, le=384000)

    @field_validator("measured_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("measured_at must include a timezone")
        return value


class MeasurementOut(MeasurementIn):
    id: int
    received_at: datetime
    model_config = ConfigDict(from_attributes=True)

