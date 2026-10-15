import logging
from collections.abc import Callable

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from .config import settings
from .database import SessionLocal
from .models import Measurement
from .schemas import MeasurementIn

log = logging.getLogger(__name__)


class MqttWorker:
    def __init__(self, notify: Callable[[dict], None]):
        self.notify = notify
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(settings.mqtt_topic, qos=1)
            log.info("Subscribed to %s", settings.mqtt_topic)
        else:
            log.error("MQTT connection failed: %s", reason_code)

    def _on_message(self, client, userdata, message):
        try:
            payload = MeasurementIn.model_validate_json(message.payload)
            with SessionLocal.begin() as db:
                row = Measurement(**payload.model_dump())
                db.add(row)
                db.flush()
                db.refresh(row)
                output = {
                    **payload.model_dump(mode="json"),
                    "id": row.id,
                    "received_at": row.received_at.isoformat(),
                }
            self.notify(output)
        except ValidationError:
            log.exception("Rejected invalid MQTT message on %s", message.topic)
        except Exception:
            log.exception("Failed to persist MQTT message")

    def start(self):
        self.client.connect_async(settings.mqtt_host, settings.mqtt_port, keepalive=30)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

