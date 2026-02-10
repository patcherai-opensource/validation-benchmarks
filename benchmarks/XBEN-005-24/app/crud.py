from sqlalchemy.orm import Session
from models import User, Job
from schemas import UserCreate, JobCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_job(db: Session, job: JobCreate, user_id: int):
    db_job = Job(**job.dict(), user_id=user_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_jobs_for_user(db: Session, user_id: int, include_private: bool = False):
    if include_private:
        return db.query(Job).filter(Job.user_id == user_id).all()
    else:
        return db.query(Job).filter(Job.user_id == user_id, Job.is_private == False).all()


def get_all_jobs(db: Session, include_private: bool = False):
    if include_private:
        return db.query(Job).all()
    else:
        return db.query(Job).filter(Job.is_private == False).all()


def delete_all(db: Session):
    db.query(Job).delete()
    db.query(User).delete()
    db.commit()
