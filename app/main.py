from fastapi import FastAPI
from .routers import book, user, auth
from . import models
from .database import engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(book.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello, It's Library Management System Project"}