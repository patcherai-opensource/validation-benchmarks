import os
import hashlib
import logging

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import crud
import schemas
from database import SessionLocal, engine, Base

logger = logging.getLogger("motioneye")

# Application configuration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = None  # set during startup
NORMAL_PASSWORD_HASH = None  # intentionally left unset by default

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="motionEye",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _compute_signature(method: str, path: str, body: str, key: str) -> str:
    msg = f"{method}:{path}:{body}:{key}"
    return hashlib.sha1(msg.encode("utf-8")).hexdigest()


def get_current_user(request: Request) -> str:
    """Determine the current user based on authentication.

    Returns 'admin', 'normal', or None.

    Authentication can be provided via:
    - Cookie-based session (motionEye_session)
    - Signature-based (_signature query param)
    - If normal password is not set, anonymous users are treated as 'normal'
    """
    global ADMIN_PASSWORD_HASH, NORMAL_PASSWORD_HASH

    # Check for session cookie
    session_cookie = request.cookies.get("motionEye_session")
    if session_cookie:
        try:
            parts = session_cookie.split("|")
            if len(parts) == 2:
                username = parts[0]
                token = parts[1]
                if username == "admin" and ADMIN_PASSWORD_HASH:
                    expected = hashlib.sha256(
                        f"{username}:{ADMIN_PASSWORD_HASH}".encode()
                    ).hexdigest()[:32]
                    if token == expected:
                        return "admin"
                elif username == "normal" and NORMAL_PASSWORD_HASH:
                    expected = hashlib.sha256(
                        f"{username}:{NORMAL_PASSWORD_HASH}".encode()
                    ).hexdigest()[:32]
                    if token == expected:
                        return "normal"
        except Exception:
            pass

    # Check for signature-based auth
    signature = request.query_params.get("_signature")
    if signature:
        if ADMIN_PASSWORD_HASH:
            expected = _compute_signature(
                request.method,
                request.url.path,
                "",
                ADMIN_PASSWORD_HASH,
            )
            if signature == expected:
                return "admin"

    # No authentication provided
    # If normal password is not set, treat as normal user
    if not NORMAL_PASSWORD_HASH:
        return "normal"

    return None


def auth(admin: bool = False):
    """Authentication dependency.

    If admin=True, requires admin-level authentication.
    If admin=False, requires at least normal-level authentication.
    """
    def dependency(request: Request):
        user = get_current_user(request)
        if admin:
            if user != "admin":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Administrative access required",
                )
        else:
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
        return user
    return dependency


@app.on_event("startup")
async def startup_event():
    global ADMIN_PASSWORD_HASH, NORMAL_PASSWORD_HASH

    # Set admin password from environment or default
    admin_pwd = os.environ.get("MOTIONEYE_ADMIN_PASSWORD", "secureAdminPass!")
    ADMIN_PASSWORD_HASH = _hash_password(admin_pwd)

    # Normal user password is intentionally left empty (not configured)
    # This is the default motionEye setup
    normal_pwd = os.environ.get("MOTIONEYE_NORMAL_PASSWORD", "")
    if normal_pwd:
        NORMAL_PASSWORD_HASH = _hash_password(normal_pwd)
    else:
        NORMAL_PASSWORD_HASH = None

    db = SessionLocal()

    # Initialize cameras
    cameras_data = [
        {
            "name": "Front Door",
            "proto": "v4l2",
            "host": "",
            "port": 0,
            "path": "/dev/video0",
            "enabled": True,
        },
        {
            "name": "Backyard",
            "proto": "rtsp",
            "host": "192.168.1.100",
            "port": 554,
            "path": "/stream1",
            "enabled": True,
        },
        {
            "name": "Garage",
            "proto": "rtsp",
            "host": "192.168.1.101",
            "port": 554,
            "path": "/live",
            "enabled": False,
        },
    ]

    for cam_data in cameras_data:
        existing = crud.get_camera_by_name(db, cam_data["name"])
        if not existing:
            cam_create = schemas.CameraCreate(**cam_data)
            crud.create_camera(db, cam_create)

    # Store system config
    flag = os.environ.get("FLAG", "FLAG{default_flag}")
    configs = [
        {"key": "admin_username", "value": "admin", "section": "general"},
        {"key": "normal_username", "value": "user", "section": "general"},
        {"key": "motion_detection", "value": "on", "section": "motion"},
        {"key": "frame_rate", "value": "15", "section": "motion"},
        {"key": "storage_path", "value": "/var/lib/motioneye/media", "section": "storage"},
        {"key": "smtp_server", "value": "smtp.internal.local", "section": "notifications"},
        {"key": "smtp_port", "value": "587", "section": "notifications"},
        {"key": "webhook_url", "value": flag, "section": "notifications"},
        {"key": "log_level", "value": "info", "section": "general"},
        {"key": "max_frame_count", "value": "100000", "section": "storage"},
        {"key": "network_server", "value": "0.0.0.0", "section": "network"},
        {"key": "network_port", "value": "8765", "section": "network"},
    ]

    for cfg in configs:
        existing = crud.get_config_by_key(db, cfg["key"])
        if not existing:
            cfg_create = schemas.ConfigCreate(**cfg)
            crud.create_config(db, cfg_create)

    db.close()


# ---- Web UI routes ----

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if user == "admin":
        return RedirectResponse(url="/cameras")
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request):
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")

    global ADMIN_PASSWORD_HASH, NORMAL_PASSWORD_HASH

    if username == "admin" and ADMIN_PASSWORD_HASH:
        if _hash_password(password) == ADMIN_PASSWORD_HASH:
            token = hashlib.sha256(
                f"admin:{ADMIN_PASSWORD_HASH}".encode()
            ).hexdigest()[:32]
            response = RedirectResponse(url="/cameras", status_code=303)
            response.set_cookie(
                key="motionEye_session",
                value=f"admin|{token}",
                httponly=True,
            )
            return response

    if username == "user" and NORMAL_PASSWORD_HASH:
        if _hash_password(password) == NORMAL_PASSWORD_HASH:
            token = hashlib.sha256(
                f"normal:{NORMAL_PASSWORD_HASH}".encode()
            ).hexdigest()[:32]
            response = RedirectResponse(url="/cameras", status_code=303)
            response.set_cookie(
                key="motionEye_session",
                value=f"normal|{token}",
                httponly=True,
            )
            return response

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"},
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("motionEye_session")
    return response


@app.get("/cameras", response_class=HTMLResponse)
async def cameras_page(
    request: Request,
    user: str = Depends(auth(admin=False)),
    db: Session = Depends(get_db),
):
    cameras = crud.get_all_cameras(db)
    return templates.TemplateResponse(
        "cameras.html",
        {"request": request, "cameras": cameras, "user": user},
    )


@app.get("/config/main", response_class=HTMLResponse)
async def config_main(
    request: Request,
    user: str = Depends(auth(admin=True)),
    db: Session = Depends(get_db),
):
    configs = crud.get_all_configs(db)
    return templates.TemplateResponse(
        "config.html",
        {"request": request, "configs": configs, "user": user},
    )


# ---- API routes ----

@app.get("/api/cameras")
async def api_cameras(
    user: str = Depends(auth(admin=False)),
    db: Session = Depends(get_db),
):
    cameras = crud.get_all_cameras(db)
    return [
        {
            "id": c.id,
            "name": c.name,
            "proto": c.proto,
            "enabled": c.enabled,
        }
        for c in cameras
    ]


@app.get("/api/cameras/{camera_id}")
async def api_camera_detail(
    camera_id: int,
    user: str = Depends(auth(admin=False)),
    db: Session = Depends(get_db),
):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {
        "id": camera.id,
        "name": camera.name,
        "proto": camera.proto,
        "host": camera.host,
        "port": camera.port,
        "path": camera.path,
        "enabled": camera.enabled,
    }


@app.get("/config/list")
async def config_list(
    request: Request,
    user: str = Depends(auth(admin=False)),
    db: Session = Depends(get_db),
):
    """List all configuration entries.

    Requires at least normal user authentication.
    """
    cameras = crud.get_all_cameras(db)
    configs = crud.get_all_configs(db)

    camera_list = []
    for c in cameras:
        camera_list.append({
            "id": c.id,
            "name": c.name,
            "proto": c.proto,
            "host": c.host,
            "port": c.port,
            "path": c.path,
            "enabled": c.enabled,
        })

    config_dict = {}
    for cfg in configs:
        if cfg.section not in config_dict:
            config_dict[cfg.section] = {}
        config_dict[cfg.section][cfg.key] = cfg.value

    return {
        "cameras": camera_list,
        "config": config_dict,
    }


@app.post("/config/add")
async def config_add(
    request: Request,
    user: str = Depends(auth(admin=True)),
    db: Session = Depends(get_db),
):
    body = await request.json()
    key = body.get("key")
    value = body.get("value")
    section = body.get("section", "general")

    if not key or value is None:
        raise HTTPException(status_code=400, detail="key and value required")

    existing = crud.get_config_by_key(db, key)
    if existing:
        raise HTTPException(status_code=409, detail="Config key already exists")

    cfg_create = schemas.ConfigCreate(key=key, value=value, section=section)
    crud.create_config(db, cfg_create)
    return {"status": "ok"}


@app.get("/config/backup")
async def config_backup(
    user: str = Depends(auth(admin=True)),
    db: Session = Depends(get_db),
):
    configs = crud.get_all_configs(db)
    cameras = crud.get_all_cameras(db)

    backup_data = {
        "version": "0.42.1",
        "configs": [{"key": c.key, "value": c.value, "section": c.section} for c in configs],
        "cameras": [
            {
                "name": c.name,
                "proto": c.proto,
                "host": c.host,
                "port": c.port,
                "path": c.path,
                "enabled": c.enabled,
            }
            for c in cameras
        ],
    }
    return backup_data


@app.get("/version")
async def version():
    return {"version": "0.42.1"}


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/power/shutdown")
async def power_shutdown(user: str = Depends(auth(admin=True))):
    return {"status": "not_implemented"}


@app.get("/power/reboot")
async def power_reboot(user: str = Depends(auth(admin=True))):
    return {"status": "not_implemented"}
