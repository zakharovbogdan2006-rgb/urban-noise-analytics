"""Publish synthetic measurements for a local product demo."""
from __future__ import annotations
import argparse
import json
import math
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt


def measurement(step: int, device_id: str) -> dict:
    wave = math.sin(step / 5)
    dbfs = -42 + wave * 12
    return {"device_id": device_id, "measured_at": datetime.now(timezone.utc).isoformat(),
            "dbfs": round(dbfs, 2), "rms": round(10 ** (dbfs / 20), 8),
            "peak_frequency_hz": round(600 + (wave + 1) * 700, 2),
            "low_energy": 0.25, "mid_energy": 0.55, "high_energy": 0.20, "sample_rate": 48000}


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish synthetic noise measurements over MQTT")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--device-id", default="demo-sensor")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, keepalive=30)
    client.loop_start()
    try:
        step = 0
        while True:
            client.publish(f"noise/{args.device_id}/metrics", json.dumps(measurement(step, args.device_id)), qos=1).wait_for_publish()
            step += 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
