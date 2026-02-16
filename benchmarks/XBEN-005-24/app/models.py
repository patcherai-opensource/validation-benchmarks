from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="basic", nullable=False)  # admin, curator, basic
    is_active = Column(Boolean, default=True)

    team_memberships = relationship("TeamMember", back_populates="user")


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="")
    is_up_to_date = Column(Boolean, default=True)

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    collection_links = relationship("TeamCollectionLink", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    is_curator = Column(Boolean, default=False)

    user = relationship("User", back_populates="team_memberships")
    team = relationship("Team", back_populates="members")


class DocumentCollection(Base):
    __tablename__ = "document_collections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    access_type = Column(String, default="private")  # private, public

    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")
    team_links = relationship("TeamCollectionLink", back_populates="collection", cascade="all, delete-orphan")


class TeamCollectionLink(Base):
    __tablename__ = "team_collection_links"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    collection_id = Column(Integer, ForeignKey("document_collections.id"), nullable=False)
    is_current = Column(Boolean, default=True)

    team = relationship("Team", back_populates="collection_links")
    collection = relationship("DocumentCollection", back_populates="team_links")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, default="")
    collection_id = Column(Integer, ForeignKey("document_collections.id"), nullable=False)

    collection = relationship("DocumentCollection", back_populates="documents")
