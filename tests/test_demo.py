from collector.demo import measurement


def test_demo_measurement_matches_ingestion_contract():
    result = measurement(1, "demo-sensor")
    assert result["device_id"] == "demo-sensor"
    assert result["sample_rate"] == 48000
    assert -160 <= result["dbfs"] <= 10
    assert result["low_energy"] + result["mid_energy"] + result["high_energy"] == 1
