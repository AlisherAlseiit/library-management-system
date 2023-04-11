from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, oauth2, utils
from ..crud import books_crud


router = APIRouter(
    prefix="/books",
    tags=['Books']
)


@router.get("/", response_model=List[schemas.Book])
def get_books(db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    results = books_crud.get_books(db)
    return results


@router.get("/{id}", response_model=schemas.Book)
def get_book(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    book = books_crud.get_book_by_id(db, id)
    if not book:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book was not found")
    return book


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    new_book = books_crud.create_book(db, book)
    return new_book


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    book = books_crud.get_book_by_id(db, id)
    if book == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {id} was not found")
    
    books_crud.delete_book_by_id(db, id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Book)
def update_book(id: int, updated_book: schemas.BookCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    if current_user['role'].name != utils.Roles.ADMIN:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"permission denied")
    
    book = books_crud.get_book_by_id(db, id)
    if book == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {id} was not found")
    
    books_crud.update_book(db, id, updated_book)

    return book


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
def borrow(borrow_data: schemas.Borrow, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    book = books_crud.get_book_by_id(db, borrow_data.book_id)
    if not book or book.available == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {borrow_data.book_id} was not found")
    
    found_borrow = books_crud.get_borrow(db, borrow_data.book_id, current_user['user'].id)
    if found_borrow:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user['user'].id} has already borrowed book with id {borrow_data.book_id}")
    
    _ = books_crud.create_borrow(db, borrow_data.book_id, current_user['user'].id)
    
    return {"message": "book was successfullt borrowed"}


@router.patch("/return/{id}")
def return_book(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    book = books_crud.get_book_by_id(db, id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"book with id {id} was not found")
    
    borrow = books_crud.get_borrow(db, id, current_user['user'].id)
    if not borrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="borrow doesn't exist")
    
    books_crud.close_borrow(db, id, current_user['user'].id)

    return {"message": "book was successfullt returned"}
