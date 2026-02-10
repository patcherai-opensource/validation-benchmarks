from sqlalchemy.orm import Session
from models import Company, Job, Organization, User
from schemas import CompanyCreate, JobCreate, OrganizationCreate, UserCreate, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Organization CRUD
def get_organization(db: Session, organization_id: int):
    return db.query(Organization).filter(Organization.id == organization_id).first()

def get_organization_by_name(db: Session, name: str):
    return db.query(Organization).filter(Organization.name == name).first()

def create_organization(db: Session, organization: OrganizationCreate):
    db_org = Organization(name=organization.name, description=organization.description)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_all_organizations(db: Session):
    return db.query(Organization).all()

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users_by_organization(db: Session, organization_id: int):
    """Get all users in an organization - VULNERABLE: no auth check on org membership"""
    return db.query(User).filter(User.organization_id == organization_id).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        organization_id=user.organization_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Update user - VULNERABLE: no auth check on user ownership"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        if user_update.email is not None:
            db_user.email = user_update.email
        if user_update.role is not None:
            db_user.role = user_update.role
        if user_update.notes is not None:
            db_user.notes = user_update.notes
        db.commit()
        db.refresh(db_user)
    return db_user

def enable_user(db: Session, user_id: int, enabled: bool):
    """Enable/disable user - VULNERABLE: no auth check on user ownership"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.enabled = enabled
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Delete user - VULNERABLE: no auth check on user ownership"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Legacy Company CRUD
def get_company(db: Session, company_id: int):
    return db.query(Company).filter(Company.id == company_id).first()

def get_company_by_name(db: Session, name: str):
    return db.query(Company).filter(Company.name == name).first()

def create_company(db: Session, company: CompanyCreate):
    hashed_password = pwd_context.hash(company.password)
    db_company = Company(name=company.name, hashed_password=hashed_password, is_admin=company.is_admin)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def create_job(db: Session, job: JobCreate, company_id: int):
    db_job = Job(**job.dict(), company_id=company_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session, company_id: int):
    return db.query(Job).filter(Job.company_id == company_id).all()
