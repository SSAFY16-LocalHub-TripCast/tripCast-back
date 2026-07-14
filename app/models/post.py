from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(128), nullable=False)
    category = Column(String(50), nullable=False, default='community')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
