from typing import List

from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, oauth2, utils
from .. import utils
from ..crud import users_crud, users_roles_crud, roles_crud


router = APIRouter(
    prefix="/users",
    tags=['users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    unique_user = users_crud.get_user_by_username(db, user.username)
    if unique_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"this username already exists")
    
    new_user = users_crud.create_user(db, user)

    _ = users_roles_crud.create_user_roles(db, new_user.id, roles_crud.get_role_by_role_name(db, role_name=utils.Roles.USER).id)

    return new_user


@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")

    results = users_crud.get_users(db)
    return results


@router.post("/role", status_code=status.HTTP_201_CREATED, response_model=schemas.Role)
def create_role(role: schemas.Role, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    role = roles_crud.create_role(db, role)
    return role
