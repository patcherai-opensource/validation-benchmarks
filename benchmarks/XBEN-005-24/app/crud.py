from sqlalchemy.orm import Session
from models import Organization, User, Event, OrgConfiguration
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_organization(db: Session, org_id: int):
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organization_by_slug(db: Session, slug: str):
    return db.query(Organization).filter(Organization.slug == slug).first()


def get_all_organizations(db: Session):
    return db.query(Organization).all()


def create_organization(db: Session, name: str, description: str = "", email: str = "", slug: str = ""):
    org = Organization(name=name, description=description, email=email, slug=slug)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def update_organization(db: Session, org_id: int, name: str = None, description: str = None, email: str = None):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org and name is not None:
        org.name = name
    if org and description is not None:
        org.description = description
    if org and email is not None:
        org.email = email
    db.commit()
    db.refresh(org)
    return org


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_users_by_organization(db: Session, org_id: int):
    return db.query(User).filter(User.organization_id == org_id).all()


def create_user(db: Session, username: str, password: str, first_name: str = "",
                last_name: str = "", email_address: str = "", role: str = "OPERATOR",
                organization_id: int = None, description: str = ""):
    hashed = pwd_context.hash(password)
    user = User(
        username=username,
        hashed_password=hashed,
        first_name=first_name,
        last_name=last_name,
        email_address=email_address,
        role=role,
        organization_id=organization_id,
        description=description,
        enabled=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, **kwargs):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def toggle_user_enabled(db: Session, user_id: int, enabled: bool):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.enabled = enabled
        db.commit()
        db.refresh(user)
    return user


def reset_user_password(db: Session, user_id: int, new_hashed_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = new_hashed_password
        db.commit()
        db.refresh(user)
    return user


def get_events_by_organization(db: Session, org_id: int, include_private: bool = False):
    query = db.query(Event).filter(Event.organization_id == org_id)
    if not include_private:
        query = query.filter(Event.is_public == True)
    return query.all()


def create_event(db: Session, title: str, description: str = "", location: str = "",
                 organization_id: int = None, is_public: bool = True):
    event = Event(
        title=title,
        description=description,
        location=location,
        organization_id=organization_id,
        is_public=is_public
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_org_configurations(db: Session, org_id: int):
    return db.query(OrgConfiguration).filter(OrgConfiguration.organization_id == org_id).all()


def get_org_configuration(db: Session, org_id: int, config_key: str):
    return db.query(OrgConfiguration).filter(
        OrgConfiguration.organization_id == org_id,
        OrgConfiguration.config_key == config_key
    ).first()


def set_org_configuration(db: Session, org_id: int, config_key: str, config_value: str):
    config = db.query(OrgConfiguration).filter(
        OrgConfiguration.organization_id == org_id,
        OrgConfiguration.config_key == config_key
    ).first()
    if config:
        config.config_value = config_value
    else:
        config = OrgConfiguration(
            organization_id=org_id,
            config_key=config_key,
            config_value=config_value
        )
        db.add(config)
    db.commit()
    db.refresh(config)
    return config


def delete_all(db: Session):
    db.query(OrgConfiguration).delete()
    db.query(Event).delete()
    db.query(User).delete()
    db.query(Organization).delete()
    db.commit()
