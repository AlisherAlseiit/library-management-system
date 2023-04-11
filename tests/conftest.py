from fastapi.testclient import TestClient
import pytest
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models, utils


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    except:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app) 


@pytest.fixture
def test_user(client):
    user_data = {"username": "alish123", "password": "123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def user_token(test_user):
    return create_access_token({"user_id": test_user['id'], "role": "user"})


@pytest.fixture
def authorized_client_user(client, user_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {user_token}"
    }

    return client


@pytest.fixture
def admin_token():
    return create_access_token({"user_id": 1, "role": "admin"})


@pytest.fixture
def authorized_client_admin(client, admin_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {admin_token}"
    }

    return client


@pytest.fixture
def add_inital_values(session):
    roles = [models.Role(**{"name": "admin"}), models.Role(**{"name": "user"})]
    session.add_all(roles)
    session.commit()

    users = [models.User(**{"username": "admin","password": f"{utils.hash('admin')}"}), 
             models.User(**{"username": "user","password": f"{utils.hash('123')}"})]
    session.add_all(users)
    session.commit()

    user_roles = [models.UserRoles(**{"user_id": 1, "role_id": 1}), models.UserRoles(**{"user_id": 2,"role_id": 2})]
    session.add_all(user_roles)
    session.commit()


@pytest.fixture
def test_books(session):
    books = [models.Book(**{"name": "Harry Potter and the Deathly Hallows","genre": "Children's Fiction"}), 
             models.Book(**{"name": "Da Vinci Code,The","genre": "Crime, Thriller & Adventure"}),
             models.Book(**{"name": "Fifty Shades of Grey","genre": "Romance & Sagas"})]
    
    session.add_all(books)
    session.commit()

    return session.query(models.Book).all()






