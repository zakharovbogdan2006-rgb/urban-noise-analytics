import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy import desc, select, text
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Measurement
from .mqtt_worker import MqttWorker
from .schemas import MeasurementOut

clients: set[WebSocket] = set()
event_loop: asyncio.AbstractEventLoop | None = None


async def broadcast(payload: dict):
    dead = []
    for socket in clients:
        try:
            await socket.send_json(payload)
        except Exception:
            dead.append(socket)
    for socket in dead:
        clients.discard(socket)


def notify(payload: dict):
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast(payload), event_loop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global event_loop
    event_loop = asyncio.get_running_loop()
    Base.metadata.create_all(engine)
    worker = MqttWorker(notify)
    worker.start()
    yield
    worker.stop()


app = FastAPI(title="Noise Monitor API", version="0.1.0", lifespan=lifespan)


def get_db():
    with SessionLocal() as db:
        yield db


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "utc_time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/measurements", response_model=list[MeasurementOut])
def measurements(
    device_id: str | None = None,
    limit: int = Query(300, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    query = select(Measurement)
    if device_id:
        query = query.where(Measurement.device_id == device_id)
    rows = db.scalars(query.order_by(desc(Measurement.measured_at)).limit(limit)).all()
    return list(reversed(rows))


@app.websocket("/ws/measurements")
async def websocket_measurements(socket: WebSocket):
    await socket.accept()
    clients.add(socket)
    try:
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        clients.discard(socket)


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).with_name("static") / "index.html")

