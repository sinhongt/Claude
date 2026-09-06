"""選擇邏輯：純函式，唔碰 I/O，所以完全可測。

兩層「最久未用」（LRU）：
1. 類別層——排除上次用過嘅類別，令連續兩次唔會同類。
2. 動作層——同一類別內先用最久未出現嘅動作，避免對固定套路麻木。

用 LRU 而唔係固定 A→B→C 循環，係為咗保留隨機感（平手時用注入嘅
rng 決定），同時仍然保證唔會連續兩次同類別。
"""

from __future__ import annotations

import random
from typing import Callable, Sequence

from .models import Activity, Category
from .state import RotationState


def choose(state: RotationState, activities: Sequence[Activity], rng: random.Random) -> Activity:
    """揀出下一個動作。"""
    if not activities:
        raise ValueError("動作庫係空嘅")
    category = choose_category(state, _categories_in(activities), rng)
    pool = [activity for activity in activities if activity.category is category]
    return _least_recently_used(pool, lambda a: state.activity_last_used.get(a.id, 0), rng)


def choose_category(
    state: RotationState, categories: Sequence[Category], rng: random.Random
) -> Category:
    """揀類別：排除上次用過嘅，再取最久未用嘅。"""
    candidates = [c for c in categories if c.value != state.last_category]
    if not candidates:  # 動作庫只得一個類別時嘅退路
        candidates = list(categories)
    return _least_recently_used(candidates, lambda c: state.category_last_used.get(c.value, 0), rng)


def _categories_in(activities: Sequence[Activity]) -> list[Category]:
    """按 Category 宣告次序回傳動作庫入面出現過嘅類別。"""
    present = {activity.category for activity in activities}
    return [category for category in Category if category in present]


def _least_recently_used(items: Sequence, key: Callable[[object], int], rng: random.Random):
    """回傳 key 最細（即最久未用；未用過為 0）者；平手用 rng 揀。"""
    lowest = min(key(item) for item in items)
    tied = [item for item in items if key(item) == lowest]
    if len(tied) == 1:
        return tied[0]
    return rng.choice(tied)
