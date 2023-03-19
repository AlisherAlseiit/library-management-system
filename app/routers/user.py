from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2, utils
from typing import List
from .. import utils

router = APIRouter(
    prefix="/users",
    tags=['users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.username == user.username)
    unique_user = user_query.first()

    if unique_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"this username already exists")
    
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_id = user_query.first().id

    role_id = db.query(models.Role).filter(models.Role.name == utils.Roles.USER).first().id

    user_roles = models.UserRoles(**{"user_id": user_id, "role_id": role_id}) 
    db.add(user_roles)
    db.commit()
    db.refresh(user_roles)

    return new_user

@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")

    results = db.query(models.User.id, models.User.username, models.User.created_at, models.Role.name.label("role")).join(
        models.UserRoles, 
        models.User.id == models.UserRoles.user_id).join(models.Role, models.Role.id == models.UserRoles.role_id).all()

    return results

@router.post("/role", status_code=status.HTTP_201_CREATED, response_model=schemas.Role)
def create_role(role: schemas.Role, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    role = models.Role(name=role.name)

    db.add(role)
    db.commit()
    db.refresh(role)

    return role
