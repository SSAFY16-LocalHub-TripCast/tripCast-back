from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    password: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: str


class PostDelete(BaseModel):
    password: str


class PostOut(PostBase):
    id: int
    category: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
