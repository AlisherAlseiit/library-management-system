from sqlalchemy.orm import Session
from .. import models, schemas, utils


def create_user_roles(db: Session, user_id: int, role_id: int):
    user_roles = models.UserRoles(**{"user_id": user_id, "role_id": role_id}) 
    db.add(user_roles)
    db.commit()
    db.refresh(user_roles)
    return user_roles