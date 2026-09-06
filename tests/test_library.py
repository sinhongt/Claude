"""全庫掃描：動作庫每次改動都要通過所有約束。"""

import pytest

from micro_recovery import formatter, validator
from micro_recovery.engine import AFFIRMATION_MAX_CHARS, MODE_CHAR_RANGE
from micro_recovery.library import ACTIVITIES, AFFIRMATIONS
from micro_recovery.models import FULL, SHORT, Category
from micro_recovery.validator import parse_duration_minutes

MIN_PER_CATEGORY = 6
RENDERINGS = [(activity, mode) for activity in ACTIVITIES for mode in (FULL, SHORT)]


def _ids(param):
    activity, mode = param
    return f"{activity.id}-{mode}"


@pytest.mark.parametrize("activity,mode", RENDERINGS, ids=[_ids(p) for p in RENDERINGS])
def test_every_rendering_satisfies_constraints(activity, mode):
    text = formatter.render(activity, mode)
    min_chars, max_chars = MODE_CHAR_RANGE[mode]
    validator.check_wording(text)
    validator.check_invitation(formatter.action_line(text))
    validator.check_length(text, min_chars=min_chars, max_chars=max_chars)


def test_activity_ids_are_unique():
    ids = [activity.id for activity in ACTIVITIES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("category", list(Category))
def test_each_category_has_enough_variety(category):
    count = sum(1 for activity in ACTIVITIES if activity.category is category)
    assert count >= MIN_PER_CATEGORY


@pytest.mark.parametrize("activity", ACTIVITIES, ids=[a.id for a in ACTIVITIES])
def test_full_duration_is_three_to_five_minutes(activity):
    assert 3 <= parse_duration_minutes(activity.duration) <= 5


@pytest.mark.parametrize("activity", ACTIVITIES, ids=[a.id for a in ACTIVITIES])
def test_short_duration_is_at_most_two_minutes(activity):
    assert 0 < parse_duration_minutes(activity.short_duration) <= 2


@pytest.mark.parametrize("affirmation", AFFIRMATIONS)
def test_affirmations_are_short_and_positive(affirmation):
    validator.check_wording(affirmation)
    validator.check_length(affirmation, min_chars=1, max_chars=AFFIRMATION_MAX_CHARS)
