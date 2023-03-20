from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2, utils
from typing import List
from datetime import datetime



router = APIRouter(
    prefix="/books",
    tags=['Books']
)

@router.get("/", response_model=List[schemas.Book])
def get_books(db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    results = db.query(models.Book).all()
    return results

@router.get("/{id}", response_model=schemas.Book)
def get_book(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == id).first()

    if not book:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book was not found")

    return book

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    book_query = db.query(models.Book).filter(models.Book.id == id)
    book = book_query.first()
    if book == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {id} was not found")

    book_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}", response_model=schemas.Book)
def update_book(id: int, updated_book: schemas.BookCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    book_query = db.query(models.Book).filter(models.Book.id == id)
    book = book_query.first()

    if book == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {id} was not found")
    
    book_query.update(updated_book.dict(), synchronize_session=False)
    db.commit()

    return book


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
def borrow(borrow_data: schemas.Borrow, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == borrow_data.book_id).first()

    if not book or book.available == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {borrow_data.book_id} was not found")
    
    
    found_borrow = db.query(models.BorrowedBooks).filter(models.BorrowedBooks.book_id == borrow_data.book_id, 
                                                         models.BorrowedBooks.user_id == current_user['user'].id,
                                                         models.BorrowedBooks.returned_at == None).first()
    
    if found_borrow:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user['user'].id} has already borrowed book with id {borrow_data.book_id}")
        

    new_borrow = models.BorrowedBooks(book_id = borrow_data.book_id, user_id = current_user['user'].id)
    db.add(new_borrow)
    db.commit()
    return {"message": "book was successfullt borrowed"}


@router.patch("/return/{id}")
def return_book(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {id} was not found")
    
    borrow_query = db.query(models.BorrowedBooks).filter(models.BorrowedBooks.book_id == id, 
                                                         models.BorrowedBooks.user_id == current_user['user'].id, 
                                                         models.BorrowedBooks.returned_at == None)
    borrow = borrow_query.first()
    if not borrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="borrow doesn't exist")
    
    borrow_query.update({"returned_at": datetime.now()}, synchronize_session=False)
    db.commit()

    return {"message": "book was successfullt returned"}
