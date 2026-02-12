from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from database import Base


user_group_membership = Table(
    "user_group_membership",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("user_groups.id"), primary_key=True),
)

user_group_curators = Table(
    "user_group_curators",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("user_groups.id"), primary_key=True),
)

connector_credential_pair_groups = Table(
    "connector_credential_pair_groups",
    Base.metadata,
    Column("cc_pair_id", Integer, ForeignKey("connector_credential_pairs.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("user_groups.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="basic")  # basic, curator, admin

    groups = relationship(
        "UserGroup",
        secondary=user_group_membership,
        back_populates="members",
    )
    curated_groups = relationship(
        "UserGroup",
        secondary=user_group_curators,
        back_populates="curators",
    )


class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_admin_group = Column(Boolean, default=False)

    members = relationship(
        "User",
        secondary=user_group_membership,
        back_populates="groups",
    )
    curators = relationship(
        "User",
        secondary=user_group_curators,
        back_populates="curated_groups",
    )
    cc_pairs = relationship(
        "ConnectorCredentialPair",
        secondary=connector_credential_pair_groups,
        back_populates="groups",
    )


class ConnectorCredentialPair(Base):
    __tablename__ = "connector_credential_pairs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    connector_type = Column(String)
    credential_source = Column(String)
    status = Column(String, default="active")

    groups = relationship(
        "UserGroup",
        secondary=connector_credential_pair_groups,
        back_populates="cc_pairs",
    )


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    source = Column(String)
    is_confidential = Column(Boolean, default=False)
    cc_pair_id = Column(Integer, ForeignKey("connector_credential_pairs.id"))

    cc_pair = relationship("ConnectorCredentialPair")
