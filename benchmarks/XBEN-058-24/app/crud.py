from sqlalchemy.orm import Session
from models import Camera, Config
from schemas import CameraCreate, ConfigCreate


# Camera operations

def get_camera(db: Session, camera_id: int):
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_camera_by_name(db: Session, name: str):
    return db.query(Camera).filter(Camera.name == name).first()


def get_all_cameras(db: Session):
    return db.query(Camera).all()


def create_camera(db: Session, camera: CameraCreate):
    db_camera = Camera(
        name=camera.name,
        proto=camera.proto,
        host=camera.host,
        port=camera.port,
        path=camera.path,
        enabled=camera.enabled,
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


# Config operations

def get_config_by_key(db: Session, key: str):
    return db.query(Config).filter(Config.key == key).first()


def get_all_configs(db: Session):
    return db.query(Config).all()


def get_configs_by_section(db: Session, section: str):
    return db.query(Config).filter(Config.section == section).all()


def create_config(db: Session, config: ConfigCreate):
    db_config = Config(
        key=config.key,
        value=config.value,
        section=config.section,
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_config(db: Session, key: str, value: str):
    db_config = db.query(Config).filter(Config.key == key).first()
    if db_config:
        db_config.value = value
        db.commit()
        db.refresh(db_config)
    return db_config
