"""狀態持久化：跨 process 都要維持輪替，而且壞檔唔可以令提醒失效。"""

import json
import random

from micro_recovery import state as state_module
from micro_recovery.engine import MicroRecoveryEngine
from micro_recovery.state import ENV_STATE_PATH, RotationState


def _engine(path, seed=3):
    return MicroRecoveryEngine(state_path=path, rng=random.Random(seed))


def test_rotation_survives_new_engine_instance(tmp_path):
    """模擬 App 每次提醒都開一個新 process。"""
    path = tmp_path / "state.json"
    first = _engine(path).trigger().category
    second = _engine(path, seed=4).trigger().category
    assert first is not second


def test_state_file_is_valid_json_with_version(tmp_path):
    path = tmp_path / "state.json"
    result = _engine(path).trigger()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["version"] == state_module.STATE_VERSION
    assert saved["last_category"] == result.category.value
    assert saved["activity_last_used"][result.activity.id] == saved["counter"] == 1


def test_corrupt_state_file_does_not_break_trigger(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{ 呢個唔係合法 JSON", encoding="utf-8")
    assert _engine(path).trigger().text


def test_unknown_version_falls_back_to_fresh_state(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"version": 999, "counter": 5}), encoding="utf-8")
    assert state_module.load(path) == RotationState()


def test_missing_file_returns_fresh_state(tmp_path):
    assert state_module.load(tmp_path / "nope.json") == RotationState()


def test_save_creates_parent_directory_and_leaves_no_temp_files(tmp_path):
    path = tmp_path / "nested" / "deep" / "state.json"
    _engine(path).trigger()
    assert path.exists()
    assert [p.name for p in path.parent.iterdir()] == ["state.json"]


def test_env_var_overrides_default_path(tmp_path, monkeypatch):
    target = tmp_path / "from-env.json"
    monkeypatch.setenv(ENV_STATE_PATH, str(target))
    assert state_module.resolve_state_path() == target
    MicroRecoveryEngine(rng=random.Random(1)).trigger()
    assert target.exists()


def test_explicit_path_wins_over_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_STATE_PATH, str(tmp_path / "from-env.json"))
    explicit = tmp_path / "explicit.json"
    assert state_module.resolve_state_path(explicit) == explicit
