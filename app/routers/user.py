from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2
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
    role_id = db.query(models.Role).filter(models.Role.name == "guest").first().id

    user_roles = models.UserRoles(**{"user_id": user_id, "role_id": role_id}) 
    db.add(user_roles)
    db.commit()
    db.refresh(user_roles)

    return new_user

@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    results = db.query(models.User).all()

    return results