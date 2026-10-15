# Collector на macOS с Python 3.13

Откройте корневую папку проекта — в ней должны находиться `pyproject.toml` и каталог `collector`.

```bash
cd /path/to/noise-monitor
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install ".[collector]"
```

Проверка зависимостей и список аудиоустройств:

```bash
python -c "import numpy, sounddevice, paho.mqtt.client; print('Dependencies OK')"
python -m collector.main --list-devices
```

Запуск, где `WINDOWS_IP` — IPv4 Windows, а `DEVICE_INDEX` — индекс микрофона:

```bash
python -m collector.main \
  --host WINDOWS_IP \
  --device-id macbook-air \
  --device DEVICE_INDEX
```

Если устройство не поддерживает 48000 Hz, добавьте `--sample-rate 44100`. Доступ к микрофону настраивается в **System Settings → Privacy & Security → Microphone**. Для проверки MQTT-соединения используйте `nc -vz WINDOWS_IP 1883`.

