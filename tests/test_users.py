import pytest
from jose import jwt

from app import schemas
from app.config import settings


def test_create_user(add_inital_values, client):
    user_res = client.post("/users/", json={"username": "alish", "password": "123"})
    new_user = schemas.UserOut(**user_res.json())
    
    assert new_user.username == "alish"
    assert user_res.status_code == 201


def test_login_user(add_inital_values, client, test_user):
    res = client.post("/login", data={"username": test_user['username'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("username, password, status_code", [
    ("wrong@gmail.com", "123", 403), 
    ("alish@gmail.com", "wrong password", 403), 
    ("wrong@gmail.com", "wrongpassword", 403), 
    (None, "password123", 422), ("alish@gmail.com", None,  422)
])
def test_incorrect_login(client, username, password, status_code):
    res = client.post("/login", data={"username": username, "password": password})
    assert res.status_code == status_code




