from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models.schemas import BookSearchRequest, CreateNarratorRequest, ChapterNarrateRequest, QARequest
from services import book_service, claude_service, session_store


app = FastAPI(title="書語人 API")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/narrator")
async def narrator_page():
    return FileResponse("static/narrator.html")


@app.get("/qa")
async def qa_page():
    return FileResponse("static/qa.html")


@app.post("/api/books/search")
async def search_books(req: BookSearchRequest):
    try:
        books = await book_service.search_books(req.query, req.search_type)
        if not books:
            return {"books": [], "message": "找不到相關書籍，請嘗試其他關鍵字"}
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"書籍搜尋服務暫時無法使用：{str(e)}")


@app.post("/api/books/create-narrator")
async def create_narrator_for_book(req: CreateNarratorRequest):
    book = req.book.model_dump()

    # Enrich with full description if currently empty
    if not book.get("description"):
        try:
            details = await book_service.fetch_book_details(book["ol_key"])
            if details.get("description"):
                book["description"] = details["description"]
            if details.get("subjects") and not book.get("subjects"):
                book["subjects"] = details["subjects"]
        except Exception:
            pass

    try:
        chapters = claude_service.synthesize_chapters(book)
        character = claude_service.create_narrator(book, chapters)
        session_id = session_store.create_session(book, character, chapters)
        return {
            "session_id": session_id,
            "book": book,
            "chapters": chapters,
            "character": character,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI 服務暫時無法使用：{str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="工作階段已過期，請重新搜尋書籍")
    return session


@app.post("/api/narrate/chapter")
async def narrate_chapter(req: ChapterNarrateRequest):
    session = session_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="工作階段已過期，請重新搜尋書籍")

    cached = session_store.get_cached_narration(req.session_id, req.chapter_number)
    if cached:
        chapter = next((c for c in session["chapters"] if c["number"] == req.chapter_number), {})
        return {"chapter_number": req.chapter_number, "chapter_title": chapter.get("title", ""), "narration": cached}

    chapter = next((c for c in session["chapters"] if c["number"] == req.chapter_number), None)
    if not chapter:
        raise HTTPException(status_code=404, detail="找不到該章節")

    try:
        narration = claude_service.narrate_chapter(session["character"], session["book"], chapter)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI 服務暫時無法使用：{str(e)}")

    session_store.cache_narration(req.session_id, req.chapter_number, narration)
    return {"chapter_number": req.chapter_number, "chapter_title": chapter["title"], "narration": narration}


@app.post("/api/qa/ask")
async def ask_question(req: QARequest):
    session = session_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="工作階段已過期，請重新搜尋書籍")

    history = session_store.get_qa_history(req.session_id)
    try:
        answer = claude_service.answer_question(
            session["character"], session["book"], req.question, history
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI 服務暫時無法使用：{str(e)}")

    session_store.append_qa(req.session_id, "user", req.question)
    session_store.append_qa(req.session_id, "assistant", answer)
    return {"answer": answer, "character_name": session["character"]["name"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
