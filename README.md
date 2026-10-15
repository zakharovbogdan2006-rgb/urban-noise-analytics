## Urban Noise Analytics Platform

**Python · PostgreSQL · FastAPI · MQTT · Docker · WebSockets · Signal Processing**

Urban Noise Analytics Platform is a distributed environmental monitoring system designed to collect, process, store, and visualize acoustic measurements in real time.

The project demonstrates an end-to-end data pipeline connecting an edge device with a containerized backend. A Python collector running on a MacBook captures microphone input in one-second intervals and performs local signal processing, including RMS calculation, dBFS estimation, frequency-domain analysis using FFT, dominant-frequency detection, and energy distribution across low-, mid-, and high-frequency bands.

Instead of transmitting raw audio, the collector sends only compact numerical measurements as JSON messages over MQTT. This keeps the data pipeline lightweight and avoids transferring or storing audio recordings.

On the server side, a Docker-based environment runs an MQTT broker, FastAPI application, and PostgreSQL database. Incoming measurements are validated and stored as time-series data, exposed through REST endpoints, and streamed to connected clients through WebSockets for real-time visualization.

The web dashboard provides live monitoring of signal levels and frequency characteristics, while the REST API and OpenAPI documentation make the collected data accessible for further analysis and integration.

### Key features

* Built a distributed real-time data pipeline from microphone acquisition to database storage and visualization.
* Implemented acoustic feature extraction using RMS measurements and FFT-based frequency analysis.
* Designed MQTT-based communication between edge and backend components with QoS 1 delivery.
* Designed structured JSON measurement messages for device-independent time-series ingestion.
* Built a FastAPI backend providing REST, WebSocket, and OpenAPI interfaces.
* Stored and queried timestamped environmental measurements in PostgreSQL.
* Containerized the backend infrastructure with Docker Compose for reproducible deployment.
* Developed a responsive dashboard for live monitoring of acoustic measurements.
* Designed the system so that raw audio remains on the acquisition device and only derived numerical metrics are transmitted.

### Architecture

**Microphone → Python signal processing → MQTT → Mosquitto → FastAPI → PostgreSQL → REST/WebSocket → Dashboard**

The current version is an MVP intended for trusted local-network deployments. Further development can include calibrated dB SPL measurements, authenticated and TLS-secured MQTT communication, time-based aggregations, threshold alerts, retention policies, and TimescaleDB-based time-series optimization.

### Quick start

Start the backend on the Windows or Linux host with Docker Desktop/Engine:

```bash
cp .env.example .env
docker compose up --build -d
```

On PowerShell, use `Copy-Item .env.example .env` instead of `cp`. The dashboard is available at `http://localhost:8000`, and OpenAPI documentation at `http://localhost:8000/docs`.

Install and run the collector on macOS with Python 3.13:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ".[collector]"
python -m collector.main --list-devices
python -m collector.main --host WINDOWS_IP --device-id macbook-air --device DEVICE_INDEX
```

Replace `WINDOWS_IP` with the backend host's private IPv4 address and `DEVICE_INDEX` with the microphone index. Both devices must be reachable on the same trusted network. See [MACOS_SETUP.md](MACOS_SETUP.md) for additional details.

### API

- `GET /health` — service and database health check
- `GET /api/v1/measurements?device_id=macbook-air&limit=300` — measurement history
- `WS /ws/measurements` — live measurements after database persistence
- `GET /docs` — interactive OpenAPI documentation

### Development

```bash
python -m pip install ".[test]"
pytest
```

The `.env` file, virtual environments, caches, and local IDE settings are excluded from Git. PostgreSQL data persists in the Docker volume until `docker compose down -v` is used.
