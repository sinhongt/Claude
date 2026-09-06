"""輪替邏輯：唔連續兩次同類別，同一動作亦唔會快速重複。"""

import random

from micro_recovery import selector
from micro_recovery.library import ACTIVITIES
from micro_recovery.models import Category
from micro_recovery.state import RotationState

ROUNDS = 30
NO_REPEAT_WINDOW = 6  # 每個類別有 6 個動作，所以窗口內唔應該撞返


def _run(rounds=ROUNDS, seed=1):
    rng = random.Random(seed)
    state = RotationState()
    picked = []
    for _ in range(rounds):
        activity = selector.choose(state, ACTIVITIES, rng)
        state.record(activity)
        picked.append(activity)
    return picked


def test_never_two_consecutive_same_category():
    picked = _run()
    categories = [activity.category for activity in picked]
    assert all(a is not b for a, b in zip(categories, categories[1:]))


def test_no_activity_repeats_within_window():
    picked = [activity.id for activity in _run()]
    for index, activity_id in enumerate(picked):
        window = picked[max(0, index - NO_REPEAT_WINDOW) : index]
        assert activity_id not in window


def test_all_categories_get_used():
    used = {activity.category for activity in _run()}
    assert used == set(Category)


def test_same_seed_reproduces_sequence():
    assert [a.id for a in _run(seed=7)] == [a.id for a in _run(seed=7)]


def test_choose_category_skips_last_used():
    state = RotationState(last_category=Category.VISUAL.value)
    rng = random.Random(0)
    for _ in range(20):
        assert selector.choose_category(state, list(Category), rng) is not Category.VISUAL


def test_single_category_library_still_returns_something():
    """退路：動作庫只得一個類別時，唔應該因為排除上次類別而揀唔到。"""
    only_visual = [a for a in ACTIVITIES if a.category is Category.VISUAL]
    state = RotationState(last_category=Category.VISUAL.value)
    assert selector.choose(state, only_visual, random.Random(0)).category is Category.VISUAL
