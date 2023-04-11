from sqlalchemy.orm import Session

from .. import models, schemas, utils


def get_role_by_role_name(db: Session, role_name: str):
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    return role


def create_role(db: Session, role: schemas.Role):
    role = models.Role(name=role.name)

    db.add(role)
    db.commit()
    db.refresh(role)
    
    return role