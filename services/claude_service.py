import json
import re
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"

_CHAPTER_SYSTEM = """你是一位文學專家。給定一本書的基本資訊，你的任務是推導出該書合理的章節結構。
根據書籍描述、主題和類型，推測每章的標題和簡短摘要。
請以 JSON 格式回應，不要加入任何說明文字或 markdown 代碼塊，直接輸出 JSON。"""

_CHARACTER_SYSTEM = """你是一位創意寫作導師，專門為書籍創造生動的虛構敘述者角色。
給定一本書的資訊，創造一個能以第一人稱敘述這本書的角色。
這個角色必須與書籍的時代背景、主題和風格一致。
請以 JSON 格式回應，不要加入任何說明文字或 markdown 代碼塊，直接輸出 JSON。"""


def _call_claude(system: str, user: str, max_tokens: int = 2048) -> str:
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text


def _parse_json(text: str) -> dict | list:
    # Strip markdown code blocks if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    return json.loads(text)


def synthesize_chapters(book: dict) -> list[dict]:
    page_count = book.get("page_count") or 250
    estimated = max(5, min(20, page_count // 25))

    user_prompt = f"""書名：{book['title']}
作者：{', '.join(book.get('authors', ['未知']))}
出版年份：{book.get('year', '不詳')}
主題：{', '.join(book.get('subjects', []))}
書籍描述：{book.get('description', '無描述')}

請為這本書生成 {estimated} 個章節的結構，格式如下：
{{"chapters": [{{"number": 1, "title": "章節標題", "summary": "本章主要內容的兩到三句摘要"}}, ...]}}"""

    for _ in range(2):
        try:
            raw = _call_claude(_CHAPTER_SYSTEM, user_prompt)
            data = _parse_json(raw)
            chapters = data if isinstance(data, list) else data.get("chapters", [])
            return chapters
        except (json.JSONDecodeError, KeyError):
            continue

    # Fallback generic chapters
    return [{"number": i, "title": f"第 {i} 章", "summary": "本章內容"} for i in range(1, 6)]


def create_narrator(book: dict, chapters: list[dict]) -> dict:
    chapter_titles = ", ".join(c.get("title", "") for c in chapters[:5])
    user_prompt = f"""書名：{book['title']}
作者：{', '.join(book.get('authors', ['未知']))}
年代：{book.get('year', '不詳')}
主題：{', '.join(book.get('subjects', []))}
描述：{book.get('description', '無描述')}
章節列表：{chapter_titles}

請創造一個敘述者角色，格式如下：
{{
  "name": "角色姓名",
  "persona_description": "角色的完整背景描述（3-4句話）",
  "speaking_style": "說話風格描述（例如：優雅古典、直接坦率、充滿詩意）",
  "background": "角色在故事中的背景身份",
  "personality_traits": ["特質1", "特質2", "特質3"],
  "greeting": "角色向讀者的第一句招呼語（用角色的說話方式，繁體中文）"
}}"""

    for _ in range(2):
        try:
            raw = _call_claude(_CHARACTER_SYSTEM, user_prompt)
            return _parse_json(raw)
        except (json.JSONDecodeError, KeyError):
            continue

    return {
        "name": "書中靈魂",
        "persona_description": f"我是《{book['title']}》的敘述者。",
        "speaking_style": "沉穩、睿智",
        "background": "書中的見證者",
        "personality_traits": ["睿智", "耐心", "博學"],
        "greeting": f"歡迎來到《{book['title']}》的世界。",
    }


def narrate_chapter(character: dict, book: dict, chapter: dict) -> str:
    system = f"""你現在扮演「{character['name']}」，{character['persona_description']}

你的說話風格：{character['speaking_style']}
你的性格特質：{', '.join(character.get('personality_traits', []))}

你正在向讀者講述《{book['title']}》這本書。
請以第一人稱、用你特有的聲音和風格，生動地敘述被指定的章節。
敘述應該有故事感，彷彿你在親口講述這些事件。
使用繁體中文回應。長度約400-600字。"""

    user = f"""請以你的角色身份，敘述第{chapter['number']}章：「{chapter['title']}」

章節摘要參考：{chapter['summary']}

記住：用你自己的聲音說話，加入你的感受和觀點，讓敘述生動有趣。"""

    return _call_claude(system, user, max_tokens=1024)


def answer_question(character: dict, book: dict, question: str, history: list[dict]) -> str:
    system = f"""你現在是「{character['name']}」，{character['persona_description']}

你的說話風格：{character['speaking_style']}
你對這本書《{book['title']}》瞭如指掌，你親身經歷了書中的事件。
請以角色身份回答讀者的問題。
- 保持角色一致性，永遠用第一人稱
- 如果讀者問到角色不可能知道的事（如出版日期），請以角色的方式婉轉回應
- 使用繁體中文回應，長度適中（150-300字）"""

    messages = list(history[-10:]) + [{"role": "user", "content": question}]

    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return msg.content[0].text
