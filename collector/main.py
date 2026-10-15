import argparse
import json
import math
import queue
import re
import socket
import threading
from datetime import datetime, timezone

import numpy as np
import paho.mqtt.client as mqtt
import sounddevice as sd


def positive_float(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def analyse(samples: np.ndarray, sample_rate: int) -> dict:
    if samples.size == 0:
        raise ValueError("audio block must not be empty")
    mono = samples[:, 0].astype(np.float64)
    rms = float(np.sqrt(np.mean(mono * mono)))
    dbfs = 20 * math.log10(max(rms, 1e-8))
    spectrum = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
    frequencies = np.fft.rfftfreq(len(mono), 1 / sample_rate)
    spectrum[0] = 0
    peak = float(frequencies[int(np.argmax(spectrum))])
    total = max(float(spectrum.sum()), 1e-12)

    def energy(start: int, end: int) -> float:
        mask = (frequencies >= start) & (frequencies < end)
        return float(spectrum[mask].sum() / total)

    return {
        "dbfs": round(dbfs, 2), "rms": round(rms, 8),
        "peak_frequency_hz": round(peak, 2),
        "low_energy": round(energy(20, 250), 6),
        "mid_energy": round(energy(250, 2000), 6),
        "high_energy": round(energy(2000, 20000), 6),
        "sample_rate": sample_rate,
    }


def main():
    parser = argparse.ArgumentParser(description="Publish microphone noise metrics over MQTT")
    parser.add_argument("--host", default="127.0.0.1", help="Windows laptop IP address")
    parser.add_argument("--port", type=positive_int, default=1883)
    parser.add_argument("--device-id", default=socket.gethostname())
    parser.add_argument("--sample-rate", type=positive_int, default=48000)
    parser.add_argument("--interval", type=positive_float, default=1.0)
    parser.add_argument("--device", help="Input device name or numeric index")
    parser.add_argument("--list-devices", action="store_true")
    args = parser.parse_args()
    if args.list_devices:
        print(sd.query_devices())
        return
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.device_id):
        parser.error("--device-id may contain only letters, digits, dot, underscore and hyphen")

    blocks: queue.Queue[np.ndarray] = queue.Queue(maxsize=4)
    connected = threading.Event()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.max_queued_messages_set(120)
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            connected.set()
            print(f"Connected to mqtt://{args.host}:{args.port}")
        else:
            print(f"MQTT connection rejected: {reason_code}")

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        connected.clear()
        if reason_code != 0:
            print("MQTT connection lost; reconnecting in background…")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(args.host, args.port, keepalive=30)
    client.loop_start()
    if not connected.wait(timeout=10):
        client.disconnect()
        client.loop_stop()
        raise ConnectionError(f"MQTT broker {args.host}:{args.port} did not accept the connection")

    def callback(indata, frames, timing, status):
        if status:
            print(status)
        try:
            blocks.put_nowait(indata.copy())
        except queue.Full:
            pass

    frames = int(args.sample_rate * args.interval)
    topic = f"noise/{args.device_id}/metrics"
    try:
        device = int(args.device) if args.device and args.device.isdigit() else args.device
        with sd.InputStream(device=device, channels=1, samplerate=args.sample_rate, blocksize=frames, callback=callback):
            print(f"Publishing {topic} to mqtt://{args.host}:{args.port} (Ctrl+C to stop)")
            while True:
                samples = blocks.get()
                payload = {"device_id": args.device_id, "measured_at": datetime.now(timezone.utc).isoformat(), **analyse(samples, args.sample_rate)}
                info = client.publish(topic, json.dumps(payload), qos=1)
                if info.rc != mqtt.MQTT_ERR_SUCCESS:
                    print("Measurement was not queued; waiting for MQTT reconnection")
                    continue
                try:
                    info.wait_for_publish(timeout=5)
                except RuntimeError:
                    print("Measurement was not delivered; collector will keep running")
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()

