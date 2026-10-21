from fastapi import FastAPI
from app.routers import books

app = FastAPI(
    title="Library Management API",
    description="Lab 4: Building CRUD Web API with FastAPI and Postman",
    version="1.0.0",
)

app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với Library Management API!"}
