from sqlalchemy.orm import Session
from models import Company, Job, Contact, Ticket, GlobalConfig
from schemas import CompanyCreate, JobCreate, ContactCreate, TicketCreate
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

def create_contact(db: Session, contact: ContactCreate):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def search_contacts_by_email(db: Session, email: str):
    return db.query(Contact).filter(Contact.email.like(email)).all()

def create_ticket(db: Session, ticket: TicketCreate, company_id: int = None):
    db_ticket = Ticket(
        subject=ticket.subject,
        message=ticket.message,
        email=ticket.email,
        company_id=company_id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_config(db: Session, name: str):
    return db.query(GlobalConfig).filter(GlobalConfig.name == name).first()

def set_config(db: Session, name: str, value: str):
    config = get_config(db, name)
    if config:
        config.value = value
    else:
        config = GlobalConfig(name=name, value=value)
        db.add(config)
    db.commit()
    return config
