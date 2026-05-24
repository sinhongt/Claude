from pydantic import BaseModel
from typing import Optional


class BookSearchRequest(BaseModel):
    query: str
    search_type: str = "title"  # "title" | "author" | "isbn"


class BookInfo(BaseModel):
    ol_key: str
    title: str
    authors: list[str] = []
    year: Optional[int] = None
    subjects: list[str] = []
    description: str = ""
    cover_url: Optional[str] = None
    page_count: Optional[int] = None


class CreateNarratorRequest(BaseModel):
    book: BookInfo


class ChapterNarrateRequest(BaseModel):
    session_id: str
    chapter_number: int


class QARequest(BaseModel):
    session_id: str
    question: str


class Chapter(BaseModel):
    number: int
    title: str
    summary: str


class Character(BaseModel):
    name: str
    persona_description: str
    speaking_style: str
    background: str
    personality_traits: list[str]
    greeting: str
