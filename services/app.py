import os
import socket
from urllib.request import urlopen

from fastapi import FastAPI
from fastapi.responses import JSONResponse


SERVICE_NAME = os.getenv("SERVICE_NAME", "service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "healthy-v1")
TCP_DEPENDENCIES = tuple(filter(None, os.getenv("TCP_DEPENDENCIES", "").split(",")))
HTTP_DEPENDENCIES = tuple(filter(None, os.getenv("HTTP_DEPENDENCIES", "").split(",")))

app = FastAPI(title=f"SentinelOps {SERVICE_NAME}")


def dependency_failures() -> list[str]:
    failures = []
    for target in TCP_DEPENDENCIES:
        host, port = target.rsplit(":", 1)
        try:
            with socket.create_connection((host, int(port)), timeout=2):
                pass
        except (OSError, ValueError) as error:
            failures.append(f"tcp://{target}: {error}")

    for url in HTTP_DEPENDENCIES:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status >= 400:
                    failures.append(f"{url}: HTTP {response.status}")
        except OSError as error:
            failures.append(f"{url}: {error}")
    return failures


@app.get("/")
def root() -> dict[str, str]:
    return {"service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/health")
def health():
    failures = dependency_failures()
    body = {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "unhealthy" if failures else "healthy",
        "failures": failures,
    }
    return JSONResponse(body, status_code=503 if failures else 200)
