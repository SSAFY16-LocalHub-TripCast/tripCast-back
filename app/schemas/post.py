from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

VALID_CATEGORIES = ["community", "travel", "food", "review"]


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    password: str
    category: str

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(VALID_CATEGORIES)}")
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: Optional[str] = None
    category: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(VALID_CATEGORIES)}")
        return value


class PostDelete(BaseModel):
    password: str


class PostPasswordCheck(BaseModel):
    password: str


class PasswordVerifyResult(BaseModel):
    valid: bool


class PostOut(PostBase):
    id: int
    category: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
