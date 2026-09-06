"""輪替狀態嘅持久化。

「唔可以連續兩次用同一類別」要跨觸發成立——App 每次提醒都係一個新
process，所以狀態一定要寫落盤。
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .models import Activity

STATE_VERSION = 1
ENV_STATE_PATH = "MICRO_RECOVERY_STATE"
DEFAULT_STATE_DIR = ".micro_recovery"
DEFAULT_STATE_FILE = "state.json"


@dataclass
class RotationState:
    """記住上次用咩類別，同每個類別／動作最後一次用嘅次序。"""

    counter: int = 0
    last_category: str | None = None
    category_last_used: dict[str, int] = field(default_factory=dict)
    activity_last_used: dict[str, int] = field(default_factory=dict)

    def record(self, activity: Activity) -> None:
        self.counter += 1
        self.last_category = activity.category.value
        self.category_last_used[activity.category.value] = self.counter
        self.activity_last_used[activity.id] = self.counter

    def to_dict(self) -> dict:
        return {
            "version": STATE_VERSION,
            "counter": self.counter,
            "last_category": self.last_category,
            "category_last_used": dict(self.category_last_used),
            "activity_last_used": dict(self.activity_last_used),
        }

    @classmethod
    def from_dict(cls, raw: object) -> "RotationState":
        """由 JSON 資料還原。格式唔啱就 raise ValueError，由 load() 處理。"""
        if not isinstance(raw, dict):
            raise ValueError("狀態檔頂層唔係 object")
        if raw.get("version") != STATE_VERSION:
            raise ValueError(f"唔識嘅狀態檔版本: {raw.get('version')!r}")
        last_category = raw.get("last_category")
        if last_category is not None and not isinstance(last_category, str):
            raise ValueError("last_category 格式唔啱")
        return cls(
            counter=int(raw.get("counter", 0)),
            last_category=last_category,
            category_last_used=_int_map(raw.get("category_last_used")),
            activity_last_used=_int_map(raw.get("activity_last_used")),
        )


def _int_map(raw: object) -> dict[str, int]:
    if not isinstance(raw, dict):
        raise ValueError("預期 object 形式嘅 last_used 紀錄")
    return {str(key): int(value) for key, value in raw.items()}


def resolve_state_path(explicit: str | os.PathLike | None = None) -> Path:
    """決定狀態檔位置：參數 > 環境變數 > 預設 ~/.micro_recovery/state.json。"""
    if explicit is not None:
        return Path(explicit).expanduser()
    from_env = os.environ.get(ENV_STATE_PATH)
    if from_env:
        return Path(from_env).expanduser()
    return Path.home() / DEFAULT_STATE_DIR / DEFAULT_STATE_FILE


def load(path: Path) -> RotationState:
    """讀取狀態。檔案唔存在、壞 JSON、或版本唔識都回傳全新狀態。

    提醒系統唔應該因為一個狀態檔壞咗就出唔到提示——最壞情況只係
    輪替由頭開始。
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return RotationState()
    try:
        return RotationState.from_dict(json.loads(raw))
    except (ValueError, TypeError):
        return RotationState()


def save(state: RotationState, path: Path) -> None:
    """原子寫入：先寫臨時檔再 os.replace()，避免中途中斷留低半截檔案。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".state-", suffix=".json")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as tmp_file:
            json.dump(state.to_dict(), tmp_file, ensure_ascii=False, indent=2)
        os.replace(tmp_name, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise
