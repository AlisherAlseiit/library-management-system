from datetime import datetime, timedelta
from typing import Annotated, List, Set

from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from pydantic import ValidationError

from . import schemas, database, models, utils
from .config import settings
from .crud import users_crud


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=utils.ALLOWED_SCOPES)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        role: str = payload.get("role")
        token_scopes = payload.get("scopes", [])
        if id == role == None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id, role=role, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise credentials_exception

    return token_data


def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": authenticate_value})

    token_data = verify_access_token(token, credentials_exception)
    user = users_crud.get_user_by_id(db, token_data.id)
    if user is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissinos",
                headers={"WWW-Authenticate": authenticate_value}
            )

    return user