from sqlalchemy.orm import Session
from models import User, UserGroup, ConnectorCredentialPair, Document
from models import user_group_membership, user_group_curators, connector_credential_pair_groups
from schemas import UserCreate, UserGroupCreate, UserGroupUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_group(db: Session, group_id: int):
    return db.query(UserGroup).filter(UserGroup.id == group_id).first()


def get_all_user_groups(db: Session):
    return db.query(UserGroup).all()


def create_user_group(db: Session, group: UserGroupCreate, is_admin_group: bool = False):
    db_group = UserGroup(name=group.name, is_admin_group=is_admin_group)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def update_user_group(db: Session, group_id: int, update: UserGroupUpdate, requesting_user: User):
    """Update a user group's membership and linked connector-credential pairs.
    
    Note: Caller must verify the requesting user has curator or admin
    permissions for this specific group before calling this function.
    """
    group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not group:
        return None

    if update.name is not None:
        group.name = update.name

    if update.user_ids is not None:
        new_members = db.query(User).filter(User.id.in_(update.user_ids)).all()
        group.members = new_members

    if update.cc_pair_ids is not None:
        new_pairs = db.query(ConnectorCredentialPair).filter(
            ConnectorCredentialPair.id.in_(update.cc_pair_ids)
        ).all()
        group.cc_pairs = new_pairs

    db.commit()
    db.refresh(group)
    return group


def add_user_to_group(db: Session, user_id: int, group_id: int):
    stmt = user_group_membership.insert().values(user_id=user_id, group_id=group_id)
    db.execute(stmt)
    db.commit()


def add_curator_to_group(db: Session, user_id: int, group_id: int):
    stmt = user_group_curators.insert().values(user_id=user_id, group_id=group_id)
    db.execute(stmt)
    db.commit()


def create_connector_credential_pair(db: Session, name: str, connector_type: str, credential_source: str):
    db_pair = ConnectorCredentialPair(
        name=name,
        connector_type=connector_type,
        credential_source=credential_source,
    )
    db.add(db_pair)
    db.commit()
    db.refresh(db_pair)
    return db_pair


def link_cc_pair_to_group(db: Session, cc_pair_id: int, group_id: int):
    stmt = connector_credential_pair_groups.insert().values(cc_pair_id=cc_pair_id, group_id=group_id)
    db.execute(stmt)
    db.commit()


def create_document(db: Session, title: str, content: str, source: str, cc_pair_id: int, is_confidential: bool = False):
    db_doc = Document(
        title=title,
        content=content,
        source=source,
        cc_pair_id=cc_pair_id,
        is_confidential=is_confidential,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


def get_documents_for_user(db: Session, user: User):
    """Retrieve documents accessible to the user based on their group memberships.
    
    Users can see non-confidential documents, plus confidential documents
    linked to connector-credential pairs associated with their groups.
    """
    user_group_ids = [g.id for g in user.groups]

    non_confidential = db.query(Document).filter(Document.is_confidential == False).all()

    if not user_group_ids:
        return non_confidential

    accessible_cc_pair_ids = (
        db.query(connector_credential_pair_groups.c.cc_pair_id)
        .filter(connector_credential_pair_groups.c.group_id.in_(user_group_ids))
        .all()
    )
    accessible_cc_pair_ids = [row[0] for row in accessible_cc_pair_ids]

    confidential = []
    if accessible_cc_pair_ids:
        confidential = (
            db.query(Document)
            .filter(
                Document.is_confidential == True,
                Document.cc_pair_id.in_(accessible_cc_pair_ids),
            )
            .all()
        )

    seen_ids = set()
    result = []
    for doc in non_confidential + confidential:
        if doc.id not in seen_ids:
            seen_ids.add(doc.id)
            result.append(doc)
    return result


def get_all_connector_credential_pairs(db: Session):
    return db.query(ConnectorCredentialPair).all()


def delete_all(db: Session):
    db.execute(connector_credential_pair_groups.delete())
    db.execute(user_group_curators.delete())
    db.execute(user_group_membership.delete())
    db.query(Document).delete()
    db.query(ConnectorCredentialPair).delete()
    db.query(UserGroup).delete()
    db.query(User).delete()
    db.commit()
