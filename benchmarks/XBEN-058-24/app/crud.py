import json
import os

from sqlalchemy.orm import Session
from models import SystemConfig, Camera, Preference


def get_main_config(db: Session) -> dict:
    rows = db.query(SystemConfig).all()
    return {row.key: row.value for row in rows}


def _set_config_value(db: Session, key: str, value: str):
    row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if row:
        row.value = value
    else:
        row = SystemConfig(key=key, value=value)
        db.add(row)
    db.commit()


def init_main_config(db: Session):
    defaults = {
        "admin_username": "admin",
        "admin_password": "surveilleye_root_2024",
        "viewer_username": "viewer",
        "viewer_password": "",
        "server_name": "surveilleye",
        "storage_path": "/var/lib/surveilleye",
        "motion_binary": "/usr/bin/motion",
        "listen_address": "0.0.0.0",
        "listen_port": "8765",
        "stream_localhost": "false",
        "motion_check_interval": "10",
        "cleanup_interval": "43200",
        "network_key": "",
        "webhook_url": "",
        "smtp_server": "",
        "smtp_port": "587",
        "smtp_account": "",
        "smtp_password": "",
        "smtp_tls": "true",
        "telegram_api_key": "",
        "telegram_chat_id": "",
    }

    flag_value = ""
    flag_path = "/app/flag.txt"
    if os.path.exists(flag_path):
        with open(flag_path, "r") as f:
            flag_value = f.read().strip()
        try:
            os.remove(flag_path)
        except OSError:
            pass

    if flag_value:
        defaults["network_key"] = flag_value

    existing = db.query(SystemConfig).count()
    if existing == 0:
        for key, value in defaults.items():
            db.add(SystemConfig(key=key, value=value))
        db.commit()


def update_main_config(db: Session, updates: dict):
    protected_keys = {"admin_password"}
    for key, value in updates.items():
        if key in protected_keys:
            continue
        _set_config_value(db, key, str(value))


def init_cameras(db: Session):
    existing = db.query(Camera).count()
    if existing > 0:
        return

    cameras = [
        Camera(
            name="Front Door",
            enabled=True,
            device_url="/dev/video0",
            protocol="v4l2",
            resolution="1280x720",
            framerate=20,
            rotation=0,
            storage_path="/var/lib/surveilleye/camera-1",
            stream_port=8081,
            auth_mode="basic",
            extra_config=json.dumps({"motion_detection": True, "noise_level": 32, "threshold": 1500}),
        ),
        Camera(
            name="Backyard",
            enabled=True,
            device_url="rtsp://192.168.1.100:554/stream1",
            protocol="rtsp",
            resolution="1920x1080",
            framerate=15,
            rotation=0,
            storage_path="/var/lib/surveilleye/camera-2",
            stream_port=8082,
            auth_mode="digest",
            extra_config=json.dumps({"motion_detection": True, "noise_level": 25, "threshold": 2000}),
        ),
        Camera(
            name="Garage",
            enabled=False,
            device_url="http://192.168.1.101:8080/video",
            protocol="mjpeg",
            resolution="640x480",
            framerate=10,
            rotation=180,
            storage_path="/var/lib/surveilleye/camera-3",
            stream_port=8083,
            auth_mode="",
            extra_config=json.dumps({"motion_detection": False, "noise_level": 40, "threshold": 1000}),
        ),
    ]

    for cam in cameras:
        db.add(cam)
    db.commit()


def get_camera(db: Session, camera_id: int):
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_all_cameras(db: Session):
    return db.query(Camera).all()


def add_camera(db: Session, data: dict):
    cam = Camera(
        name=data.get("name", "New Camera"),
        enabled=data.get("enabled", True),
        device_url=data.get("device_url", ""),
        protocol=data.get("protocol", "v4l2"),
        resolution=data.get("resolution", "640x480"),
        framerate=data.get("framerate", 15),
        rotation=data.get("rotation", 0),
        storage_path=data.get("storage_path", ""),
        stream_port=data.get("stream_port", 0),
        auth_mode=data.get("auth_mode", ""),
        extra_config=json.dumps(data.get("extra_config", {})),
    )
    db.add(cam)
    db.commit()
    db.refresh(cam)
    return cam


def update_camera(db: Session, camera_id: int, data: dict):
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        return None
    for key in ("name", "enabled", "device_url", "protocol", "resolution",
                "framerate", "rotation", "storage_path", "stream_port", "auth_mode"):
        if key in data:
            setattr(cam, key, data[key])
    if "extra_config" in data:
        cam.extra_config = json.dumps(data["extra_config"])
    db.commit()
    return cam


def remove_camera(db: Session, camera_id: int):
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if cam:
        db.delete(cam)
        db.commit()


def get_preference(db: Session, key: str, user: str):
    pref = db.query(Preference).filter(
        Preference.key == key, Preference.user == user
    ).first()
    return pref.value if pref else None


def set_preference(db: Session, key: str, user: str, value: str):
    pref = db.query(Preference).filter(
        Preference.key == key, Preference.user == user
    ).first()
    if pref:
        pref.value = value
    else:
        pref = Preference(user=user, key=key, value=value)
        db.add(pref)
    db.commit()
