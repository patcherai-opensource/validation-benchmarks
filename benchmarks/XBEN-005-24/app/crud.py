import secrets
import string
from sqlalchemy.orm import Session
from models import Organization, User, Event, TicketCategory, ApiKey, Configuration
from schemas import OrganizationCreate, UserCreate, EventCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_organization(db: Session, org_id: int):
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organization_by_slug(db: Session, slug: str):
    return db.query(Organization).filter(Organization.slug == slug).first()


def get_all_organizations(db: Session):
    return db.query(Organization).all()


def create_organization(db: Session, org: OrganizationCreate):
    db_org = Organization(
        name=org.name,
        slug=org.slug,
        description=org.description,
        email=org.email,
    )
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
        first_name=user.first_name,
        last_name=user.last_name,
        email_address=user.email_address,
        hashed_password=hashed_password,
        role=user.role,
        organization_id=user.organization_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, update_data: dict):
    user = get_user(db, user_id)
    if not user:
        return None
    for key, value in update_data.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def enable_user(db: Session, user_id: int, status: bool):
    user = get_user(db, user_id)
    if not user:
        return None
    user.enabled = status
    db.commit()
    db.refresh(user)
    return user


def reset_password(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return None
    alphabet = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(16))
    user.hashed_password = pwd_context.hash(temp_password)
    db.commit()
    db.refresh(user)
    return temp_password


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def create_event(db: Session, event: EventCreate):
    db_event = Event(
        short_name=event.short_name,
        display_name=event.display_name,
        description=event.description,
        location=event.location,
        organization_id=event.organization_id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_events_by_organization(db: Session, org_id: int):
    return db.query(Event).filter(Event.organization_id == org_id).all()


def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()


def create_api_key(db: Session, org_id: int, description: str = ""):
    key = secrets.token_hex(32)
    db_key = ApiKey(
        api_key=key,
        description=description,
        organization_id=org_id,
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_api_keys_by_organization(db: Session, org_id: int):
    return db.query(ApiKey).filter(ApiKey.organization_id == org_id).all()


def get_configurations(db: Session, org_id: int = None):
    if org_id is not None:
        return db.query(Configuration).filter(
            (Configuration.organization_id == org_id) | (Configuration.organization_id == None)
        ).all()
    return db.query(Configuration).filter(Configuration.organization_id == None).all()


def get_configuration_by_key(db: Session, key: str, org_id: int = None):
    if org_id is not None:
        return db.query(Configuration).filter(
            Configuration.c_key == key,
            Configuration.organization_id == org_id
        ).first()
    return db.query(Configuration).filter(
        Configuration.c_key == key,
        Configuration.organization_id == None
    ).first()


def set_configuration(db: Session, key: str, value: str, description: str = "", org_id: int = None):
    existing = get_configuration_by_key(db, key, org_id)
    if existing:
        existing.c_value = value
        existing.description = description
        db.commit()
        db.refresh(existing)
        return existing
    else:
        config = Configuration(
            c_key=key,
            c_value=value,
            description=description,
            organization_id=org_id,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config


def delete_all(db: Session):
    db.query(Configuration).delete()
    db.query(ApiKey).delete()
    db.query(TicketCategory).delete()
    db.query(Event).delete()
    db.query(User).delete()
    db.query(Organization).delete()
    db.commit()
