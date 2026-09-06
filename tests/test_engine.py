"""引擎：模式判定、輸出格式、被打斷時嘅語氣。"""

import random
import re

import pytest

from micro_recovery.engine import MODE_CHAR_RANGE, MicroRecoveryEngine, resolve_mode
from micro_recovery.models import FULL, SHORT
from micro_recovery.validator import BANNED_CONSEQUENCE, BANNED_IMPERATIVE, BANNED_JARGON

OUTPUT_PATTERN = re.compile(
    r"^【今日微休息】\n▸ 動作：.+\n▸ 時間：.+\n▸ 提示：.+$",
)


@pytest.fixture
def engine(tmp_path):
    return MicroRecoveryEngine(state_path=tmp_path / "state.json", rng=random.Random(11))


@pytest.mark.parametrize(
    "minutes,expected",
    [(None, FULL), (1, SHORT), (2, SHORT), (2.5, FULL), (5, FULL), (60, FULL)],
)
def test_resolve_mode(minutes, expected):
    assert resolve_mode(minutes) == expected


@pytest.mark.parametrize("minutes", [0, -1])
def test_resolve_mode_rejects_non_positive_time(minutes):
    with pytest.raises(ValueError):
        resolve_mode(minutes)


def test_output_follows_fixed_format(engine):
    assert OUTPUT_PATTERN.match(engine.trigger().text)


def test_full_output_is_sixty_to_ninety_chars(engine):
    result = engine.trigger()
    low, high = MODE_CHAR_RANGE[FULL]
    assert low <= result.char_count <= high


def test_short_mode_is_not_padded(engine):
    result = engine.trigger(available_minutes=1)
    low, high = MODE_CHAR_RANGE[SHORT]
    assert result.mode == SHORT
    assert low <= result.char_count <= high


def test_more_than_five_minutes_does_not_lengthen_output(engine):
    """超過 5 分鐘只提供核心動作，唔會刻意加長內容填滿時間。"""
    generous = engine.trigger(available_minutes=30)
    low, high = MODE_CHAR_RANGE[FULL]
    assert generous.mode == FULL
    assert low <= generous.char_count <= high


def test_interrupted_adds_affirmation_without_blame(engine):
    result = engine.trigger(interrupted=True)
    assert result.affirmation is not None
    assert result.text.startswith(result.affirmation)
    assert OUTPUT_PATTERN.match(result.text.split("\n", 1)[1])
    for phrase in BANNED_CONSEQUENCE:
        assert phrase not in result.text


def test_interrupted_does_not_count_affirmation_in_char_budget(engine):
    result = engine.trigger(interrupted=True)
    low, high = MODE_CHAR_RANGE[FULL]
    assert low <= result.char_count <= high


def test_normal_trigger_has_no_affirmation(engine):
    assert engine.trigger().affirmation is None


@pytest.mark.parametrize("minutes,interrupted", [(None, False), (1, False), (None, True)])
def test_no_banned_wording_in_any_mode(engine, minutes, interrupted):
    text = engine.trigger(available_minutes=minutes, interrupted=interrupted).text
    for phrase in BANNED_IMPERATIVE + BANNED_CONSEQUENCE + BANNED_JARGON:
        assert phrase not in text


def test_consecutive_triggers_rotate_categories(engine):
    categories = [engine.trigger().category for _ in range(10)]
    assert all(a is not b for a, b in zip(categories, categories[1:]))
