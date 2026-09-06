"""微休息系統的資料模型。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

FULL = "full"
SHORT = "short"


class Category(str, Enum):
    """三個休息類別。連續兩次觸發唔可以用同一個。"""

    VISUAL = "視覺休息"
    STRETCH = "身體伸展"
    BREATH = "呼吸放鬆"


@dataclass(frozen=True)
class Activity:
    """一個微休息動作，包含完整版（3-5 分鐘）同壓縮版（1-2 分鐘）。

    壓縮版係獨立設計嘅最低門檻動作，唔係完整版嘅縮寫——時間唔多時
    只做一件事，好過趕住做完三件事。
    """

    id: str
    category: Category
    action: str
    duration: str
    tip: str
    short_action: str
    short_duration: str
    short_tip: str

    def variant(self, mode: str) -> tuple[str, str, str]:
        """回傳 (動作, 時間, 提示)。mode 為 FULL 或 SHORT。"""
        if mode == FULL:
            return self.action, self.duration, self.tip
        if mode == SHORT:
            return self.short_action, self.short_duration, self.short_tip
        raise ValueError(f"未知模式: {mode!r}")


@dataclass(frozen=True)
class Break:
    """一次觸發嘅結果。"""

    activity: Activity
    category: Category
    mode: str
    text: str
    char_count: int
    affirmation: str | None = None
