"""引擎：串起狀態 → 選擇 → 渲染 → 驗證 → 寫回狀態。"""

from __future__ import annotations

import os
import random
from typing import Sequence

from . import formatter, selector, state, validator
from .library import ACTIVITIES, AFFIRMATIONS
from .models import FULL, SHORT, Activity, Break

# 完整版沿用規格嘅 60-90 字。
# 壓縮版下調至 30-60：規格明言 1-2 分鐘唔好強行塞滿 3-5 分鐘嘅設計，
# 硬套 60 字下限只會迫內容膨脹。
MODE_CHAR_RANGE: dict[str, tuple[int, int]] = {
    FULL: (60, 90),
    SHORT: (30, 60),
}

# 只得 1-2 分鐘就切去最短版本
SHORT_MODE_MAX_MINUTES = 2.0

# 肯定句係核心區塊以外嘅一句話，唔計入 60-90 字評估
AFFIRMATION_MAX_CHARS = 24


def resolve_mode(available_minutes: float | None) -> str:
    """由可用時間決定模式。

    - 冇講時間 → 完整版（3-5 分鐘）
    - 1-2 分鐘 → 壓縮版（單一最低門檻動作）
    - 超過 5 分鐘 → 仍然只出完整版，唔會刻意加長內容填滿時間
    """
    if available_minutes is None:
        return FULL
    if available_minutes <= 0:
        raise ValueError("可用時間要大過 0 分鐘")
    if available_minutes <= SHORT_MODE_MAX_MINUTES:
        return SHORT
    return FULL


class MicroRecoveryEngine:
    """每次被觸發時產生一個微休息指令。

    狀態寫落 JSON 檔，所以即使每次提醒都係新 process，類別輪替
    （唔連續兩次同類）同動作去重都仍然成立。
    """

    def __init__(
        self,
        *,
        state_path: str | os.PathLike | None = None,
        activities: Sequence[Activity] = ACTIVITIES,
        affirmations: Sequence[str] = AFFIRMATIONS,
        rng: random.Random | None = None,
    ) -> None:
        self.state_path = state.resolve_state_path(state_path)
        self._activities = tuple(activities)
        self._affirmations = tuple(affirmations)
        self._rng = rng if rng is not None else random.Random()

    def trigger(
        self, available_minutes: float | None = None, interrupted: bool = False
    ) -> Break:
        """產生一次微休息指令，並更新輪替狀態。"""
        mode = resolve_mode(available_minutes)
        current = state.load(self.state_path)
        activity = selector.choose(current, self._activities, self._rng)

        core = formatter.render(activity, mode)
        affirmation = self._rng.choice(self._affirmations) if interrupted else None
        text = formatter.with_affirmation(core, affirmation)
        self._enforce_constraints(core, text, mode, affirmation)

        current.record(activity)
        state.save(current, self.state_path)

        return Break(
            activity=activity,
            category=activity.category,
            mode=mode,
            text=text,
            char_count=validator.count_chars(core),
            affirmation=affirmation,
        )

    def _enforce_constraints(
        self, core: str, text: str, mode: str, affirmation: str | None
    ) -> None:
        """輸出前最後一道閘。違反就 raise ConstraintViolation。"""
        validator.check_wording(text)
        validator.check_invitation(formatter.action_line(core))
        min_chars, max_chars = MODE_CHAR_RANGE[mode]
        validator.check_length(core, min_chars=min_chars, max_chars=max_chars)
        if affirmation is not None:
            validator.check_length(affirmation, min_chars=1, max_chars=AFFIRMATION_MAX_CHARS)
