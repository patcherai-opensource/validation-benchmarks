from sqlalchemy.orm import Session
from models import User, Team, TeamMember, DocumentCollection, TeamCollectionLink, Document
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str, role: str = "basic"):
    hashed_password = pwd_context.hash(password)
    db_user = User(email=email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_team(db: Session, team_id: int):
    return db.query(Team).filter(Team.id == team_id).first()


def get_all_teams(db: Session):
    return db.query(Team).all()


def get_teams_for_user(db: Session, user_id: int, only_curator_teams: bool = False):
    query = (
        db.query(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .filter(TeamMember.user_id == user_id)
    )
    if only_curator_teams:
        query = query.filter(TeamMember.is_curator == True)
    return query.all()


def create_team(db: Session, name: str, description: str = ""):
    db_team = Team(name=name, description=description)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def add_team_member(db: Session, team_id: int, user_id: int, is_curator: bool = False):
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    if existing:
        return existing
    member = TeamMember(team_id=team_id, user_id=user_id, is_curator=is_curator)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_team_member(db: Session, team_id: int, user_id: int):
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    if member:
        db.delete(member)
        db.commit()


def get_team_members(db: Session, team_id: int):
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()


def create_collection(db: Session, name: str, description: str = "", access_type: str = "private"):
    collection = DocumentCollection(name=name, description=description, access_type=access_type)
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def link_team_collection(db: Session, team_id: int, collection_id: int):
    existing = db.query(TeamCollectionLink).filter(
        TeamCollectionLink.team_id == team_id,
        TeamCollectionLink.collection_id == collection_id
    ).first()
    if existing:
        return existing
    link = TeamCollectionLink(team_id=team_id, collection_id=collection_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def unlink_team_collection(db: Session, team_id: int, collection_id: int):
    link = db.query(TeamCollectionLink).filter(
        TeamCollectionLink.team_id == team_id,
        TeamCollectionLink.collection_id == collection_id
    ).first()
    if link:
        db.delete(link)
        db.commit()


def get_collections_for_team(db: Session, team_id: int):
    return (
        db.query(DocumentCollection)
        .join(TeamCollectionLink, TeamCollectionLink.collection_id == DocumentCollection.id)
        .filter(TeamCollectionLink.team_id == team_id, TeamCollectionLink.is_current == True)
        .all()
    )


def get_accessible_collections_for_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []

    if user.role == "admin":
        return db.query(DocumentCollection).all()

    team_ids = [tm.team_id for tm in user.team_memberships]
    if not team_ids:
        return db.query(DocumentCollection).filter(DocumentCollection.access_type == "public").all()

    private_collections = (
        db.query(DocumentCollection)
        .join(TeamCollectionLink, TeamCollectionLink.collection_id == DocumentCollection.id)
        .filter(
            TeamCollectionLink.team_id.in_(team_ids),
            TeamCollectionLink.is_current == True
        )
        .all()
    )
    public_collections = db.query(DocumentCollection).filter(DocumentCollection.access_type == "public").all()

    seen_ids = set()
    result = []
    for c in private_collections + public_collections:
        if c.id not in seen_ids:
            seen_ids.add(c.id)
            result.append(c)
    return result


def get_documents_in_collection(db: Session, collection_id: int):
    return db.query(Document).filter(Document.collection_id == collection_id).all()


def create_document(db: Session, title: str, content: str, collection_id: int):
    doc = Document(title=title, content=content, collection_id=collection_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_collection(db: Session, collection_id: int):
    return db.query(DocumentCollection).filter(DocumentCollection.id == collection_id).first()


def delete_all(db: Session):
    db.query(TeamCollectionLink).delete()
    db.query(TeamMember).delete()
    db.query(Document).delete()
    db.query(DocumentCollection).delete()
    db.query(Team).delete()
    db.query(User).delete()
    db.commit()
