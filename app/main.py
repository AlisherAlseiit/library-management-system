from fastapi import FastAPI
from .routers import book, user, auth
from . import models
from .database import engine

app = FastAPI()

# models.Base.metadata.create_all(bind=engine)

app.include_router(book.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello, it's my library management system"}