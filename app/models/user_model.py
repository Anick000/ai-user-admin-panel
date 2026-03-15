from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: str
    name: str
    email: str


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None