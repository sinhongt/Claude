"""約束檢查本身嘅測試。"""

import pytest

from micro_recovery import validator
from micro_recovery.validator import ConstraintViolation

SAMPLE = "【今日微休息】\n▸ 動作：可以慢慢眨眼10次\n▸ 時間：1分鐘\n▸ 提示：眼睛就鬆返"


def test_count_chars_excludes_structure_and_whitespace():
    # 標題、【】▸：同換行都唔計，淨低 23 個字：
    # 「動作可以慢慢眨眼10次」11 +「時間1分鐘」5 +「提示眼睛就鬆返」7
    assert validator.count_chars(SAMPLE) == 23


def test_count_chars_ignores_blank_text():
    assert validator.count_chars("【今日微休息】\n\n  ") == 0


@pytest.mark.parametrize(
    "phrase",
    validator.BANNED_IMPERATIVE + validator.BANNED_CONSEQUENCE + validator.BANNED_JARGON,
)
def test_every_banned_phrase_is_caught(phrase):
    with pytest.raises(ConstraintViolation):
        validator.check_wording(f"提示：{phrase}")


def test_clean_text_passes_wording():
    validator.check_wording("不妨慢慢眨眼10次，眼睛就鬆返少少")


@pytest.mark.parametrize("marker", validator.INVITATION_MARKERS)
def test_invitation_markers_accepted(marker):
    validator.check_invitation(f"▸ 動作：{marker}慢慢眨眼10次")


def test_missing_invitation_is_caught():
    with pytest.raises(ConstraintViolation):
        validator.check_invitation("▸ 動作：慢慢眨眼10次")


def test_length_bounds_are_inclusive():
    text = "一二三四五"
    validator.check_length(text, min_chars=5, max_chars=5)
    with pytest.raises(ConstraintViolation):
        validator.check_length(text, min_chars=6, max_chars=10)
    with pytest.raises(ConstraintViolation):
        validator.check_length(text, min_chars=1, max_chars=4)


@pytest.mark.parametrize(
    "text,expected",
    [("3分鐘", 3.0), ("4分鐘", 4.0), ("30秒", 0.5), ("90秒", 1.5)],
)
def test_parse_duration_minutes(text, expected):
    assert validator.parse_duration_minutes(text) == expected


@pytest.mark.parametrize("text", ["三分鐘", "3 mins", "", "3分鐘左右"])
def test_parse_duration_rejects_unknown_format(text):
    with pytest.raises(ConstraintViolation):
        validator.parse_duration_minutes(text)
