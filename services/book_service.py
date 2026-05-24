import httpx
from typing import Optional

OPEN_LIBRARY_SEARCH = "https://openlibrary.org/search.json"
OPEN_LIBRARY_WORKS = "https://openlibrary.org/works/{key}.json"
GOOGLE_BOOKS_SEARCH = "https://www.googleapis.com/books/v1/volumes"
COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"

FIELDS = "key,title,author_name,first_publish_year,subject,number_of_pages_median,cover_i"


async def search_books(query: str, search_type: str) -> list[dict]:
    params: dict = {"fields": FIELDS, "limit": 5}
    if search_type == "author":
        params["author"] = query
    elif search_type == "isbn":
        params["isbn"] = query
    else:
        params["q"] = query

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(OPEN_LIBRARY_SEARCH, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for doc in data.get("docs", []):
        ol_key = doc.get("key", "")
        cover_id = doc.get("cover_i")
        results.append({
            "ol_key": ol_key,
            "title": doc.get("title", "未知書名"),
            "authors": doc.get("author_name", []),
            "year": doc.get("first_publish_year"),
            "subjects": doc.get("subject", [])[:5],
            "description": "",
            "cover_url": COVER_URL.format(cover_id=cover_id) if cover_id else None,
            "page_count": doc.get("number_of_pages_median"),
        })
    return results


async def fetch_book_details(ol_key: str) -> dict:
    # ol_key is like "/works/OL12345W" — strip leading slash for URL
    key = ol_key.lstrip("/")
    url = f"https://openlibrary.org/{key}.json"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return {}
        data = resp.json()

    description = _extract_description(data)

    # Fall back to Google Books if no description
    if not description:
        title = data.get("title", "")
        description = await _google_books_description(title)

    subjects = []
    for s in data.get("subjects", []):
        if isinstance(s, str):
            subjects.append(s)
        elif isinstance(s, dict):
            subjects.append(s.get("name", ""))
    subjects = subjects[:8]

    return {
        "description": description,
        "subjects": subjects,
    }


def _extract_description(work_data: dict) -> str:
    desc = work_data.get("description", "")
    if isinstance(desc, str):
        return desc
    if isinstance(desc, dict):
        return desc.get("value", "")
    return ""


async def _google_books_description(title: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(GOOGLE_BOOKS_SEARCH, params={"q": title, "maxResults": 1})
            data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0].get("volumeInfo", {}).get("description", "")
    except Exception:
        pass
    return ""
