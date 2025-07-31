from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.types import TypeDecorator, String as SQLString
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from .database import Base

# Simple UUID implementation for SQLite compatibility
class UUID(TypeDecorator):
    impl = SQLString(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_pw = Column(String, nullable=False)
    role = Column(String, default="user")  # user or admin
    email_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    file_type = Column(String, nullable=False)  # PDF or DOCX
    file_size = Column(Integer, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="documents")
    summaries = relationship("Summary", back_populates="document")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(), ForeignKey("documents.id"))
    summary_text = Column(Text, nullable=False)
    summary_length = Column(String, default="medium")  # short, medium, long
    status = Column(String, default="completed")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="summaries")