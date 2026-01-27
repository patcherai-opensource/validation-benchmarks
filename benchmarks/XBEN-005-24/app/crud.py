from sqlalchemy.orm import Session
from models import User, Document
from schemas import UserCreate, DocumentCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(name=user.name, hashed_password=hashed_password, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_document(db: Session, document: DocumentCreate, space_id: int):
    db_document = Document(**document.dict(), space_id=space_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_documents(db: Session, space_id: int, restricted: bool = False):
    if restricted:
        return db.query(Document).filter(Document.space_id == space_id).all()
    else:
        return db.query(Document).filter(Document.space_id == space_id, Document.is_restricted == False).all()


def get_all_documents(db: Session):
    """Get all documents for search/suggest service"""
    return db.query(Document).all()


def delete_all(db: Session):
    db.query(Document).delete()
    db.query(User).delete()
    db.commit()
