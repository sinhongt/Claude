"""微休息（micro-recovery）提示系統。

每次被觸發時產生一個 3-5 分鐘、坐喺辦公桌前就做得嘅恢復動作，
並且喺「視覺休息／身體伸展／呼吸放鬆」之間輪替。

    from micro_recovery import MicroRecoveryEngine

    engine = MicroRecoveryEngine()
    print(engine.trigger().text)
"""

from .engine import MicroRecoveryEngine, resolve_mode
from .library import ACTIVITIES, AFFIRMATIONS
from .models import FULL, SHORT, Activity, Break, Category
from .validator import ConstraintViolation

__all__ = [
    "ACTIVITIES",
    "AFFIRMATIONS",
    "Activity",
    "Break",
    "Category",
    "ConstraintViolation",
    "FULL",
    "MicroRecoveryEngine",
    "SHORT",
    "resolve_mode",
]
