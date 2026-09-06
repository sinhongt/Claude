"""把約束條件寫成可執行檢查，而唔係註釋。

休息本身唔應該成為新嘅壓力來源，所以語氣同用詞唔可以靠人手記住——
動作庫每次改動都會經呢度掃一次（見 tests/test_library.py）。
"""

from __future__ import annotations

import re

# 命令式或帶壓力嘅語氣，一律改用邀請式
BANNED_IMPERATIVE = ("你應該", "你需要", "你必須", "你一定要", "記住要", "務必", "應該要")

# 暗示「唔做／做唔完就會點點點」嘅負面後果語言
BANNED_CONSEQUENCE = (
    "否則",
    "唔做就",
    "如果唔",
    "會導致",
    "浪費",
    "唔夠",
    "做得唔",
    "後果",
    "失敗",
    "半途而廢",
)

# 醫學／生理術語，提示句只用生活化語言
BANNED_JARGON = (
    "睫狀肌",
    "副交感",
    "交感神經",
    "自律神經",
    "皮質",
    "血氧",
    "腦血流",
    "生理喚醒",
    "肌張力",
)

# 邀請式語氣嘅標記，動作句至少要有一個
INVITATION_MARKERS = ("不妨", "可以", "試下", "嘗試", "有興趣")

HEADER_TITLE = "今日微休息"
STRUCTURAL_CHARS = "【】▸：:"


class ConstraintViolation(ValueError):
    """輸出違反約束條件。"""


def count_chars(text: str) -> int:
    """計算內容字數。

    排除結構符號（`【】▸：`）、標題「今日微休息」同所有空白，
    只計實際內容——包括「動作」「時間」「提示」三個標籤本身。
    咁樣 60-90 字嘅要求就有客觀、可測嘅定義。
    """
    body = text.replace(HEADER_TITLE, "")
    return len([ch for ch in body if ch not in STRUCTURAL_CHARS and not ch.isspace()])


def check_wording(text: str) -> None:
    """擋住命令式語氣、負面後果語言同醫學術語。"""
    for label, phrases in (
        ("命令式語氣", BANNED_IMPERATIVE),
        ("負面後果語言", BANNED_CONSEQUENCE),
        ("醫學術語", BANNED_JARGON),
    ):
        for phrase in phrases:
            if phrase in text:
                raise ConstraintViolation(f"{label}「{phrase}」出現於：{text!r}")


def check_invitation(text: str) -> None:
    """確認有邀請式語氣嘅標記。"""
    if not any(marker in text for marker in INVITATION_MARKERS):
        raise ConstraintViolation(f"缺少邀請式語氣（{'／'.join(INVITATION_MARKERS)}）：{text!r}")


def check_length(text: str, *, min_chars: int, max_chars: int) -> None:
    """確認內容字數落在指定範圍。"""
    count = count_chars(text)
    if not min_chars <= count <= max_chars:
        raise ConstraintViolation(f"內容字數 {count} 唔喺 {min_chars}-{max_chars} 之間：{text!r}")


def validate(text: str, *, min_chars: int, max_chars: int) -> None:
    """一次過跑齊所有檢查。"""
    check_wording(text)
    check_invitation(text)
    check_length(text, min_chars=min_chars, max_chars=max_chars)


_DURATION_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)(分鐘|秒)$")


def parse_duration_minutes(duration: str) -> float:
    """把「3分鐘」「30秒」轉成分鐘數，方便檢查時間範圍。"""
    match = _DURATION_PATTERN.match(duration.strip())
    if not match:
        raise ConstraintViolation(f"時間格式唔識: {duration!r}")
    value = float(match.group(1))
    return value if match.group(2) == "分鐘" else value / 60
