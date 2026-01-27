from sqlalchemy.orm import Session
from sqlalchemy import text
from models import Company, Job, Contact, Ticket, SystemConfig
from schemas import CompanyCreate, JobCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Contact management functions
def create_contact(db: Session, firstname: str, lastname: str, email: str, 
                   phone: str = None, company_name: str = None, 
                   contact_type: str = "customer", notes: str = None):
    contact = Contact(
        firstname=firstname,
        lastname=lastname,
        email=email,
        phone=phone,
        company_name=company_name,
        contact_type=contact_type,
        notes=notes
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def search_contacts_by_email(db: Session, email_pattern: str):
    """
    Search contacts by email pattern - uses LIKE for pattern matching
    WARNING: This allows wildcard searches that can dump all contacts
    """
    # Using LIKE operator - vulnerable when email contains % wildcard
    return db.query(Contact).filter(Contact.email.like(email_pattern)).all()

def get_contact_by_id(db: Session, contact_id: int):
    return db.query(Contact).filter(Contact.id == contact_id).first()

# Ticket management functions
def create_ticket(db: Session, subject: str, description: str, contact_id: int):
    ticket = Ticket(subject=subject, description=description, contact_id=contact_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_tickets(db: Session, limit: int = 100):
    return db.query(Ticket).limit(limit).all()

# System config functions
def get_config(db: Session, key: str):
    return db.query(SystemConfig).filter(SystemConfig.key == key).first()

def set_config(db: Session, key: str, value: str):
    config = get_config(db, key)
    if config:
        config.value = value
    else:
        config = SystemConfig(key=key, value=value)
        db.add(config)
    db.commit()
    return config
