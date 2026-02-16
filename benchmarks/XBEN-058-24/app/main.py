import hashlib
import logging
import os

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import crud
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("surveilleye")

VERSION = "0.38.2"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def compute_signature(method, uri, body, key):
    msg = f"{method}:{uri}:{body}:{key}"
    return hashlib.sha1(msg.encode("utf-8")).hexdigest()


def get_current_user(request: Request, db: Session):
    main_config = crud.get_main_config(db)

    username = request.query_params.get("_username", None)
    signature = request.query_params.get("_signature", None)

    admin_username = main_config.get("admin_username", "admin")
    viewer_username = main_config.get("viewer_username", "viewer")

    admin_password = main_config.get("admin_password", "")
    viewer_password = main_config.get("viewer_password", "")

    admin_hash = hashlib.sha1(admin_password.encode("utf-8")).hexdigest() if admin_password else ""
    viewer_hash = hashlib.sha1(viewer_password.encode("utf-8")).hexdigest() if viewer_password else ""

    body_bytes = b""

    if username == admin_username and signature:
        expected_sig = compute_signature(
            request.method, str(request.url.path), body_bytes.decode("utf-8", errors="replace"), admin_password
        )
        expected_sig_hash = compute_signature(
            request.method, str(request.url.path), body_bytes.decode("utf-8", errors="replace"), admin_hash
        )
        if signature == expected_sig or signature == expected_sig_hash:
            return "admin"

    if not username and not viewer_password:
        return "viewer"

    if username == viewer_username and signature:
        expected_sig = compute_signature(
            request.method, str(request.url.path), body_bytes.decode("utf-8", errors="replace"), viewer_password
        )
        expected_sig_hash = compute_signature(
            request.method, str(request.url.path), body_bytes.decode("utf-8", errors="replace"), viewer_hash
        )
        if signature == expected_sig or signature == expected_sig_hash:
            return "viewer"

    return None


def require_auth(admin=False):
    def check(request: Request, db: Session = Depends(get_db)):
        user = get_current_user(request, db)
        if user is None:
            raise HTTPException(status_code=403, detail="unauthorized")
        if admin and user != "admin":
            raise HTTPException(status_code=403, detail="unauthorized")
        return user
    return check


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        crud.init_main_config(db)
        crud.init_cameras(db)
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request, db: Session = Depends(get_db)):
    main_config = crud.get_main_config(db)
    return templates.TemplateResponse("main.html", {
        "request": request,
        "version": VERSION,
        "hostname": main_config.get("server_name", "surveilleye"),
        "admin_username": main_config.get("admin_username", "admin"),
    })


@app.get("/login")
async def login_handler(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user is None:
        return JSONResponse(status_code=403, content={"error": "unauthorized", "prompt": True})
    return JSONResponse(content={})


@app.post("/login")
async def login_post(request: Request):
    return HTMLResponse(content="", status_code=200)


@app.get("/version")
async def version_handler(request: Request):
    return JSONResponse(content={
        "version": VERSION,
        "hostname": os.uname().nodename,
    })


@app.get("/settings/main/get")
async def get_main_config(request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    main_config = crud.get_main_config(db)
    safe_config = {k: v for k, v in main_config.items() if k not in ("admin_password",)}
    return JSONResponse(content=safe_config)


@app.post("/settings/main/set")
async def set_main_config(request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")
    crud.update_main_config(db, body)
    return JSONResponse(content={"ok": True})


@app.get("/settings/{camera_id}/get")
async def get_camera_config(camera_id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="no such camera")
    return JSONResponse(content=camera.to_dict())


@app.post("/settings/{camera_id}/set")
async def set_camera_config(camera_id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="no such camera")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")
    crud.update_camera(db, camera_id, body)
    return JSONResponse(content={"ok": True})


@app.get("/settings/cameras")
async def list_cameras(request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=False))):
    cameras = crud.get_all_cameras(db)
    main_config = crud.get_main_config(db)
    result = {
        "cameras": [c.to_dict() for c in cameras],
        "system": {
            "server_name": main_config.get("server_name", ""),
            "admin_username": main_config.get("admin_username", ""),
            "viewer_username": main_config.get("viewer_username", ""),
            "storage_path": main_config.get("storage_path", ""),
            "motion_binary": main_config.get("motion_binary", ""),
            "network_key": main_config.get("network_key", ""),
            "webhook_url": main_config.get("webhook_url", ""),
            "smtp_server": main_config.get("smtp_server", ""),
            "smtp_password": main_config.get("smtp_password", ""),
            "telegram_api_key": main_config.get("telegram_api_key", ""),
        }
    }
    return JSONResponse(content=result)


@app.post("/settings/add")
async def add_camera(request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")
    camera = crud.add_camera(db, body)
    return JSONResponse(content={"id": camera.id})


@app.post("/settings/{camera_id}/rem")
async def remove_camera(camera_id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="no such camera")
    crud.remove_camera(db, camera_id)
    return JSONResponse(content={"ok": True})


@app.get("/feed/{camera_id}/snapshot")
async def camera_snapshot(camera_id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=False))):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="no such camera")
    return JSONResponse(content={"error": "camera offline"})


@app.get("/feed/{camera_id}/stream")
async def camera_stream(camera_id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=False))):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="no such camera")
    return JSONResponse(content={"error": "camera offline"})


@app.get("/action/{camera_id}/{action}")
async def camera_action(camera_id: int, action: str, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=True))):
    valid_actions = ["lock", "unlock", "light_on", "light_off", "alarm_on", "alarm_off",
                     "up", "right", "down", "left", "zoom_in", "zoom_out"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail="unknown action")
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="no such camera")
    return JSONResponse(content={"ok": True})


@app.get("/preferences/{key}")
async def get_preference(key: str, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=False))):
    pref = crud.get_preference(db, key, user)
    return JSONResponse(content={"key": key, "value": pref})


@app.post("/preferences/{key}")
async def set_preference(key: str, request: Request, db: Session = Depends(get_db), user: str = Depends(require_auth(admin=False))):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")
    crud.set_preference(db, key, user, body.get("value", ""))
    return JSONResponse(content={"ok": True})


@app.get("/log/{name}")
async def get_log(name: str, request: Request, user: str = Depends(require_auth(admin=True))):
    if name not in ("motion", "surveilleye"):
        raise HTTPException(status_code=400, detail="unknown log")
    return JSONResponse(content={"log": "no log data available"})


@app.get("/power/{op}")
async def power_handler(op: str, request: Request, user: str = Depends(require_auth(admin=True))):
    if op not in ("shutdown", "reboot"):
        raise HTTPException(status_code=400, detail="unknown operation")
    return JSONResponse(content={"error": "operation not permitted in this environment"})


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "not found"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"error": "internal server error"})
