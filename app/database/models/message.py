# Created: dylannguyen
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from pgvector.sqlalchemy import Vector
from app.database.database import Base
from sqlalchemy.orm import relationship


class Sessions(Base):
    __tablename__ = 'SYS_SESSIONS'
    id = Column(Integer, primary_key= True, index = True)
    session_id = Column(String, unique=True, nullable=False)
    messages = relationship("Messages", back_populates="session", cascade="all, delete-orphan")

class Messages(Base):
    __tablename__ = 'SYS_MESSAGES'
    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey('SYS_SESSIONS.session_id'), nullable = False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector, nullable=True) # Embedding as a vector
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    session = relationship("Sessions", back_populates="messages")
    
    