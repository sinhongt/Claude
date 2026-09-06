"""渲染固定輸出格式。

格式係對外契約（App 可能靠佢做解析），所以集中喺一處，並由測試用
regex 鎖死行數同標籤。
"""

from __future__ import annotations

from .models import Activity

HEADER = "【今日微休息】"
BULLET = "▸"
LABEL_ACTION = "動作"
LABEL_DURATION = "時間"
LABEL_TIP = "提示"


def render(activity: Activity, mode: str) -> str:
    """渲染【今日微休息】核心區塊。"""
    action, duration, tip = activity.variant(mode)
    return "\n".join(
        (
            HEADER,
            f"{BULLET} {LABEL_ACTION}：{action}",
            f"{BULLET} {LABEL_DURATION}：{duration}",
            f"{BULLET} {LABEL_TIP}：{tip}",
        )
    )


def with_affirmation(core: str, affirmation: str | None) -> str:
    """被打斷嘅情況下，喺區塊前面加一句簡短肯定。"""
    if not affirmation:
        return core
    return f"{affirmation}\n{core}"


def action_line(text: str) -> str:
    """抽出動作句（連標籤），用嚟做語氣檢查。"""
    prefix = f"{BULLET} {LABEL_ACTION}："
    for line in text.splitlines():
        if line.startswith(prefix):
            return line
    return ""
