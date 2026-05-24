import uuid
from typing import Optional

_store: dict[str, dict] = {}


def create_session(book: dict, character: dict, chapters: list[dict]) -> str:
    session_id = str(uuid.uuid4())
    _store[session_id] = {
        "session_id": session_id,
        "book": book,
        "character": character,
        "chapters": chapters,
        "narration_cache": {},
        "qa_history": [],
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    return _store.get(session_id)


def cache_narration(session_id: str, chapter_number: int, narration: str) -> None:
    if session_id in _store:
        _store[session_id]["narration_cache"][str(chapter_number)] = narration


def get_cached_narration(session_id: str, chapter_number: int) -> Optional[str]:
    session = _store.get(session_id)
    if session:
        return session["narration_cache"].get(str(chapter_number))
    return None


def append_qa(session_id: str, role: str, content: str) -> None:
    if session_id in _store:
        history = _store[session_id]["qa_history"]
        history.append({"role": role, "content": content})
        # Keep last 20 turns
        if len(history) > 20:
            _store[session_id]["qa_history"] = history[-20:]


def get_qa_history(session_id: str) -> list[dict]:
    session = _store.get(session_id)
    return session["qa_history"] if session else []
