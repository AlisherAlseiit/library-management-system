import pytest
from jose import jwt
from app import schemas, models
from app.config import settings




def test_get_all_books(add_inital_values, authorized_client_user):
    res = authorized_client_user.get("/books/")
    assert res.status_code == 200

def test_unauthorized_user_get_all_books(client):
    res = client.get("/books/")
    assert res.status_code == 401

def test_get_one_book(add_inital_values, authorized_client_user, test_books):
    res = authorized_client_user.get(f"/books/{test_books[0].id}")
    assert res.status_code == 200

def test_unauthorized_get_one_book(client, test_books):
    res = client.get(f"/books/{test_books[0].id}")
    assert res.status_code == 401

def test_get_one_book_not_exist(add_inital_values, authorized_client_user):
    res = authorized_client_user.get(f"/books/976654")
    assert res.status_code == 404


@pytest.mark.parametrize("name, genre", [
    ("Twilight", "Young Adult Fiction"),
    ("Harry Potter and the Deathly Hallows", "Children's Fiction"),
    ("Da Vinci Code,The", "Crime, Thriller & Adventure")
    ])
def test_admin_create_book(add_inital_values, authorized_client_admin, name, genre):
    res = authorized_client_admin.post("/books/", json={"name": name, "genre": genre})

    created_book = schemas.Book(**res.json())
    assert created_book.name == name
    assert created_book.genre == genre
    assert res.status_code == 201

def test_unauthorized_create_book(client):
    res = client.post("/books/", json={"name": "name", "genre": "genre"})
    assert res.status_code == 401

def test_user_create_book(add_inital_values, authorized_client_user):
    res = authorized_client_user.post("/books/", json={"name": "name", "genre": "genre"})
    assert res.status_code == 403


def test_admin_delete_book(add_inital_values, authorized_client_admin, test_books):
    res = authorized_client_admin.delete(f"/books/{test_books[0].id}")
    assert res.status_code == 204

def test_unauthorized_user_delete_book(client, test_books):
    res = client.delete(f"/books/{test_books[0].id}")
    assert res.status_code == 401

def test_user_delete_book(add_inital_values, authorized_client_user, test_books):
    res = authorized_client_user.delete(f"/books/{test_books[0].id}")
    assert res.status_code == 403

def test_delete_book_non_exist(add_inital_values, authorized_client_admin):
    res = authorized_client_admin.delete(f"/books/254287")
    assert res.status_code == 404


def test_admin_update_book(add_inital_values, authorized_client_admin, test_books):
    data = {
        "name": "Saga",
        "genre": "fantasy"
    }
    res = authorized_client_admin.put(f"/books/{test_books[0].id}", json=data)
    assert res.status_code == 200

def test_unauthorized_user_update_book(client, test_books):
    data = {
        "name": "Saga",
        "genre": "fantasy"
    }
    res = client.put(f"/books/{test_books[0].id}", json=data)
    assert res.status_code == 401

def test_user_update_book(add_inital_values, authorized_client_user, test_books):
    data = {
        "name": "Saga",
        "genre": "fantasy"
    }
    res = authorized_client_user.put(f"/books/{test_books[0].id}", json=data)
    assert res.status_code == 403

def test_update_book_non_exist(add_inital_values, authorized_client_admin):
    data = {
        "name": "Saga",
        "genre": "fantasy"
    }
    res = authorized_client_admin.put(f"/books/18239", json=data)
    assert res.status_code == 404


@pytest.fixture
def test_borrow(test_books, session, test_user):
    new_borrow = models.BorrowedBooks(book_id=test_books[0].id, user_id=test_user['id'])
    session.add(new_borrow)
    session.commit()

def test_user_borrow_book(add_inital_values, authorized_client_user, test_books):
    res = authorized_client_user.post("/books/borrow", json={"book_id": test_books[0].id})
    assert res.status_code == 201

def test_borrow_twice_book(add_inital_values, authorized_client_user, test_books, test_borrow):
    res = authorized_client_user.post("/books/borrow", json={"book_id": test_books[0].id})
    assert res.status_code == 409

def test_unauthorized_user_borrow_book(client, test_books):
    res = client.post("/books/borrow", json={"book_id": test_books[0].id})
    assert res.status_code == 401

def test_borrow_book_non_exist(add_inital_values, authorized_client_user):
    res = authorized_client_user.post("/books/borrow", json={"book_id": 8000})
    assert res.status_code == 404


def test_user_return_book(add_inital_values, authorized_client_user, test_books, test_borrow):
    res = authorized_client_user.patch(f"/books/return/{test_books[0].id}")
    assert res.status_code == 200

def test_unauthorized_user_return_book(client, test_books):
    res = client.patch(f"/books/return/{test_books[0].id}")
    assert res.status_code == 401

def test_return_book_non_exist(add_inital_values, authorized_client_user):
    res = authorized_client_user.patch("/books/return/12492")
    assert res.status_code == 404
