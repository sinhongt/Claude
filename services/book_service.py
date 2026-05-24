import re
import json
import subprocess

_CLI = "claude"
_CLI_CWD = "/tmp"

_SEARCH_SYSTEM = """你是一位博學的書籍專家，熟知各類文學作品。
根據使用者的查詢，列出最多5本最相關的書籍。
以JSON格式回應，不要加任何說明文字或markdown代碼塊，直接輸出JSON。"""


def _call(system: str, user: str) -> str:
    cmd = [
        _CLI, "-p",
        "--system-prompt", system,
        "--no-session-persistence",
        "--output-format", "text",
        "--model", "claude-haiku-4-5-20251001",
    ]
    result = subprocess.run(
        cmd,
        input=user,
        capture_output=True,
        text=True,
        cwd=_CLI_CWD,
        timeout=60,
    )
    return result.stdout.strip()


def _parse_json(text: str):
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)


async def search_books(query: str, search_type: str) -> list[dict]:
    if search_type == "author":
        msg = f"請列出作者「{query}」最著名的5本書，優先列出最具代表性的作品"
    elif search_type == "isbn":
        msg = f"請找出ISBN為「{query}」的書籍資訊，若找不到則列出最相近的書"
    else:
        msg = f"""用戶搜尋：「{query}」
請優先列出書名完全符合或高度相似「{query}」的書籍（例如若搜尋 'Harry Potter' 應優先列出哈利波特系列），再補充相關書籍，共列出5本。"""

    msg += """

請以以下JSON格式回應（繁體中文描述）：
{
  "books": [
    {
      "title": "書名（繁體中文或原文）",
      "authors": ["作者姓名"],
      "year": 出版年份（數字或null）,
      "description": "書籍簡介，100-150字，繁體中文",
      "subjects": ["主題標籤1", "主題標籤2", "主題標籤3"],
      "page_count": 估計頁數（數字或null）
    }
  ]
}"""

    raw = _call(_SEARCH_SYSTEM, msg)
    data = _parse_json(raw)
    books = data.get("books", [])

    for i, book in enumerate(books):
        slug = str(book.get("title", "")).replace(" ", "_")[:20]
        book["ol_key"] = f"ai_{i}_{slug}"
        book.setdefault("cover_url", None)
        book.setdefault("description", "")
        book.setdefault("subjects", [])
        book.setdefault("authors", [])
        book.setdefault("page_count", None)

    return books


async def fetch_book_details(ol_key: str) -> dict:
    # All details already provided by search_books
    return {}
