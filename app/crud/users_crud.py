from sqlalchemy.orm import Session

from .. import models, schemas, utils


def get_user_by_username(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    return user


def get_user_by_id(db: Session, id: int):
    user = db.query(models.User, models.Role.name.label("role")).join(models.UserRoles, 
    models.User.id == models.UserRoles.user_id).join(models.Role, models.Role.id == models.UserRoles.role_id).filter(models.User.id == id).first()

    return user


def get_users(db: Session):
    return db.query(models.User.id, models.User.username, models.User.created_at, models.Role.name.label("role")).join(
        models.UserRoles, 
        models.User.id == models.UserRoles.user_id).join(models.Role, models.Role.id == models.UserRoles.role_id).all()


def create_user(db: Session, user: schemas.UserCreate):
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
