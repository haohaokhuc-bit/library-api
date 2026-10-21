from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, Query, status
from app.data import BOOKS
from app.models import BookCreate, BookOut, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])
BookId = Annotated[int, Path(gt=0, description="Mã sách")]

def find_book(book_id: int) -> dict:
    for b in BOOKS:
        if b["id"] == book_id:
            return b
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sách không tồn tại")

def check_isbn(isbn: str, exclude_id: int | None = None) -> None:
    for b in BOOKS:
        if b["isbn"] == isbn and b["id"] != exclude_id:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Mã ISBN đã tồn tại")

@router.get("", response_model=list[BookOut])
def get_books(
    q: str | None = Query(default=None, description="Tìm theo tên sách"),
    author: str | None = Query(default=None, description="Lọc theo tác giả"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    result = BOOKS
    if q:
        result = [b for b in result if q.lower() in b["title"].lower()]
    if author:
        result = [b for b in result if author.lower() in b["author"].lower()]
    return result[skip : skip + limit]

@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: BookId):
    return find_book(book_id)

@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    check_isbn(book.isbn)
    new_id = max((b["id"] for b in BOOKS), default=0) + 1
    new_book = book.model_dump()
    new_book["id"] = new_id
    BOOKS.append(new_book)
    return new_book

@router.put("/{book_id}", response_model=BookOut)
def update_book_full(book_id: BookId, book: BookCreate):
    existing = find_book(book_id)
    check_isbn(book.isbn, exclude_id=book_id)
    updated_data = book.model_dump()
    updated_data["id"] = book_id
    idx = BOOKS.index(existing)
    BOOKS[idx] = updated_data
    return updated_data

@router.patch("/{book_id}", response_model=BookOut)
def update_book_partial(book_id: BookId, book: BookUpdate):
    existing = find_book(book_id)
    update_data = book.model_dump(exclude_unset=True)
    if "isbn" in update_data:
        check_isbn(update_data["isbn"], exclude_id=book_id)
    existing.update(update_data)
    return existing

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: BookId):
    existing = find_book(book_id)
    BOOKS.remove(existing)
    return None
