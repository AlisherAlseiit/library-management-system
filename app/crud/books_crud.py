from datetime import datetime

from sqlalchemy.orm import Session

from .. import models, schemas, utils


def get_borrow_query(db: Session, book_id: int, user_id: int):
    query = db.query(models.BorrowedBooks).filter(models.BorrowedBooks.book_id == book_id, 
                                                         models.BorrowedBooks.user_id == user_id,
                                                         models.BorrowedBooks.returned_at == None)
    return query


def get_book_query(db: Session, id: int):
    query = db.query(models.Book).filter(models.Book.id == id)
    return query
    

def get_books(db: Session):
    return db.query(models.Book).all()


def get_book_by_id(db: Session, id: int):
    book = get_book_query(db, id).first()
    return book


def create_book(db: Session, book: schemas.BookCreate):
    new_book = models.Book(**book.dict())

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book


def delete_book_by_id(db: Session, id: int):
    get_book_query(db, id).delete(synchronize_session=False)
    db.commit()


def update_book(db: Session, id: int, updated_book: schemas.BookCreate):
    get_book_query(db, id).update(updated_book.dict(), synchronize_session=False)
    db.commit()


def get_borrow(db: Session, book_id: int, user_id: int):
    borrow = get_borrow_query(db, book_id, user_id).first()
    return borrow


def create_borrow(db: Session, book_id: int, user_id: int):
    new_borrow = models.BorrowedBooks(book_id = book_id, user_id = user_id)

    db.add(new_borrow)
    db.commit()
    
    return new_borrow


def close_borrow(db: Session, book_id: int, user_id: int):
    get_borrow_query(db, book_id, user_id).update({"returned_at": datetime.now()}, synchronize_session=False)
    db.commit()