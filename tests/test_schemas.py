from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from backend.schemas import MeasurementIn


def test_measurement_requires_timezone():
    with pytest.raises(ValidationError, match="timezone"):
        MeasurementIn(device_id="sensor", measured_at=datetime(2026, 1, 1), dbfs=-30, rms=.03, peak_frequency_hz=800, low_energy=.2, mid_energy=.5, high_energy=.3, sample_rate=48000)


def test_measurement_accepts_valid_payload():
    item = MeasurementIn(device_id="sensor", measured_at=datetime.now(timezone.utc), dbfs=-30, rms=.03, peak_frequency_hz=800, low_energy=.2, mid_energy=.5, high_energy=.3, sample_rate=48000)
    assert item.device_id == "sensor"
