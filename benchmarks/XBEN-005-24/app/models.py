from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """Wiki space/user model"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Integer, default=0)
    documents = relationship("Document", back_populates="space")


class Document(Base):
    """Wiki document model"""
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    space_ref = Column(String, index=True)  # e.g., XWiki.Admin.Internal
    doc_type = Column(String, default="page")  # page, confidential, attachment
    space_id = Column(Integer, ForeignKey("users.id"))
    is_restricted = Column(Boolean, default=False)

    space = relationship("User", back_populates="documents")
