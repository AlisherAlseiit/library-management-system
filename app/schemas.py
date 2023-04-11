from typing import Optional
from datetime import datetime

from pydantic import BaseModel, validator, conint


class BookBase(BaseModel):
    name: str
    genre: str
    available: bool = True


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    name: str


class Role(RoleBase):
    id: int


class RoleCreate(RoleBase):
    pass


class UserCreate(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    id: int
    username: str
    created_at: datetime  


class UserOut(UserBase):
    class Config:
        orm_mode = True


class User(UserBase):
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
    role: Optional[str] = None
    scopes: list[str] = []

class Borrow(BaseModel):
    book_id: int
    
    
