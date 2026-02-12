"""Internal metadata service - not publicly accessible."""

import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI()


def read_flag():
    try:
        with open("/app/flag.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "FLAG{default_placeholder}"


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "internal metadata service v1.0"


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "ok"


@app.get("/latest/meta-data/", response_class=JSONResponse)
async def metadata_root():
    return {
        "instance-id": "i-0a1b2c3d4e5f67890",
        "instance-type": "ml.g4dn.xlarge",
        "local-ipv4": "10.0.1.42",
        "placement": {"availability-zone": "us-west-2a"},
        "services": ["iam", "secrets"],
    }


@app.get("/latest/meta-data/iam/", response_class=JSONResponse)
async def metadata_iam():
    return {
        "info": {
            "role": "gradio-app-service-role",
            "last-updated": "2024-01-15T08:30:00Z",
        }
    }


@app.get("/latest/meta-data/secrets/", response_class=JSONResponse)
async def metadata_secrets():
    flag = read_flag()
    return {
        "app-secret-key": flag,
        "database-url": "postgresql://gradio:internal@db.cluster.local:5432/gradio_prod",
        "model-api-key": "sk-prod-xxxxxxxxxxxxxxxxxxxx",
    }


@app.get("/latest/meta-data/identity-credentials/", response_class=JSONResponse)
async def metadata_identity():
    flag = read_flag()
    return {
        "access-key-id": "AKIA4EXAMPLE",
        "secret-access-key": flag,
        "token": "FwoGZXIvYXdzEBYaDH...",
        "expiration": "2024-12-31T23:59:59Z",
    }
