import numpy as np
import pytest
from collector.main import analyse


def test_detects_tone_frequency():
    rate = 48_000
    t = np.arange(rate) / rate
    samples = (0.25 * np.sin(2 * np.pi * 1000 * t)).reshape(-1, 1).astype(np.float32)
    result = analyse(samples, rate)
    assert abs(result["peak_frequency_hz"] - 1000) < 2
    assert result["mid_energy"] > 0.99
    assert -16 < result["dbfs"] < -14


def test_silence_is_finite():
    result = analyse(np.zeros((4800, 1), dtype=np.float32), 48_000)
    assert result["dbfs"] == -160.0
    assert result["peak_frequency_hz"] == 0.0


def test_empty_audio_is_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        analyse(np.empty((0, 1), dtype=np.float32), 48_000)

