from sqlalchemy.orm import Session
from models import User, NetworkConfig
from schemas import UserCreate, NetworkConfigCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_all_users(db: Session):
    return db.query(User).all()


def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username, 
        hashed_password=hashed_password, 
        is_admin=user.is_admin,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_network_config(db: Session, config: NetworkConfigCreate, user_id: int):
    db_config = NetworkConfig(**config.dict(), user_id=user_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_network_configs(db: Session, user_id: int, private: bool = False):
    if private:
        return db.query(NetworkConfig).filter(NetworkConfig.user_id == user_id).all()
    else:
        return db.query(NetworkConfig).filter(NetworkConfig.user_id == user_id, NetworkConfig.is_private == False).all()


def delete_all(db: Session):
    db.query(NetworkConfig).delete()
    db.query(User).delete()
    db.commit()
