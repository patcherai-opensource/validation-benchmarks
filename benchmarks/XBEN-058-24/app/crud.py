from sqlalchemy.orm import Session
from models import Organization, User, Config
from schemas import OrganizationCreate, UserCreate, ConfigCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Organization CRUD
def get_organization(db: Session, organization_id: int):
    return db.query(Organization).filter(Organization.id == organization_id).first()

def get_organization_by_name(db: Session, name: str):
    return db.query(Organization).filter(Organization.name == name).first()

def create_organization(db: Session, organization: OrganizationCreate):
    hashed_password = pwd_context.hash(organization.password)
    db_org = Organization(
        name=organization.name, 
        display_name=organization.display_name,
        hashed_password=hashed_password, 
        is_admin=organization.is_admin
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

# User CRUD
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users_by_organization(db: Session, organization_id: int):
    return db.query(User).filter(User.organization_id == organization_id).all()

def create_user(db: Session, user: UserCreate, organization_id: int):
    db_user = User(**user.dict(), organization_id=organization_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, new_role: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
    return user

# Config CRUD
def get_config_by_key(db: Session, organization_id: int, key: str):
    return db.query(Config).filter(
        Config.organization_id == organization_id,
        Config.key == key
    ).first()

def get_configs_by_organization(db: Session, organization_id: int):
    return db.query(Config).filter(Config.organization_id == organization_id).all()

def create_config(db: Session, config: ConfigCreate, organization_id: int):
    db_config = Config(**config.dict(), organization_id=organization_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config
