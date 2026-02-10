from sqlalchemy.orm import Session
from models import Organization, User, Secret
from schemas import OrganizationCreate, UserCreate, SecretCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_organization(db: Session, org_id: int):
    return db.query(Organization).filter(Organization.id == org_id).first()

def get_organization_by_name(db: Session, name: str):
    return db.query(Organization).filter(Organization.name == name).first()

def create_organization(db: Session, org: OrganizationCreate):
    db_org = Organization(name=org.name, description=org.description)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users_by_organization(db: Session, org_id: int):
    return db.query(User).filter(User.organization_id == org_id).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password,
        organization_id=user.organization_id,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def toggle_user_enabled(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.enabled = not user.enabled
        db.commit()
        db.refresh(user)
    return user

def get_secrets_by_organization(db: Session, org_id: int):
    return db.query(Secret).filter(Secret.organization_id == org_id).all()

def create_secret(db: Session, secret: SecretCreate, org_id: int):
    db_secret = Secret(key=secret.key, value=secret.value, organization_id=org_id)
    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)
    return db_secret
