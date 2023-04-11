from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, schemas, models, utils, oauth2
from ..crud import users_crud


router = APIRouter(
    tags=['Authantication']
)


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = users_crud.get_user_by_username(db, user_credentials.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    role = db.query(models.Role).join(models.UserRoles, models.Role.id == models.UserRoles.role_id).filter(models.UserRoles.user_id == user.id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user role was not found")

    access_token = oauth2.create_access_token(data={"user_id": user.id, "role": role.name})
    
    return {"access_token": access_token, "token_type": "bearer"}

