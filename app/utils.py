from enum import Enum

from passlib.context import CryptContext


pwd_contenxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_contenxt.hash(password)


def verify(plain_password, hash_password):
    return pwd_contenxt.verify(plain_password, hash_password)

ALLOWED_SCOPES = {
    "books:read": "This scope allows users to view the list of books in the library.", 
    "books:borrow": "This scope allows users to borrow books from the library.", 
    "books:return": "This scope allows users to return books to the library."}

def validate_scopes(scopes: list[str]):
    return set(scopes).issubset(ALLOWED_SCOPES.keys()) 


class Roles(str, Enum):
    USER= "user"
    ADMIN = "admin"