from typing import Optional
from pydantic import BaseModel, validator, conint
from datetime import datetime
import itertools

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
    
class Role(BaseModel):
    id: int
    name: str

class RoleCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str
    

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    username: str
    created_at: datetime
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    role: Optional[str] = None


class Borrow(BaseModel):
    book_id: int
    
    
