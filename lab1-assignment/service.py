

import socket
import time
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Lab Assignment 1 Service")

start_time = time.time()


@app.get("/info")
def info(delay: float = 0.0):

    if delay > 0:
        time.sleep(delay)

    return {
        "host": socket.gethostname(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health(delay: float = 0.0):
    """Return service status and uptime."""

    if delay > 0:
        time.sleep(delay)

    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - start_time, 2),
    }
