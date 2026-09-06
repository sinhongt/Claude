"""命令列入口，可以直接掛落定時提醒或 App 觸發。

    python -m micro_recovery                # 預設 3-5 分鐘
    python -m micro_recovery --minutes 1    # 只得 1-2 分鐘
    python -m micro_recovery --interrupted  # 做到中途被打斷
    python -m micro_recovery --json         # 方便 App 解析
"""

from __future__ import annotations

import argparse
import json
import random
import sys

from .engine import MicroRecoveryEngine
from .validator import ConstraintViolation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="micro_recovery",
        description="產生一個 3-5 分鐘嘅微休息指令",
    )
    parser.add_argument(
        "--minutes",
        type=float,
        default=None,
        help="今次可用嘅分鐘數；1-2 分鐘會自動出壓縮版",
    )
    parser.add_argument(
        "--interrupted",
        action="store_true",
        help="做到中途被打斷，輸出會加一句簡短肯定",
    )
    parser.add_argument(
        "--state",
        default=None,
        help="輪替狀態檔路徑（預設 ~/.micro_recovery/state.json）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="固定隨機種子，方便測試同重現",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    engine = MicroRecoveryEngine(
        state_path=args.state,
        rng=random.Random(args.seed) if args.seed is not None else None,
    )

    try:
        result = engine.trigger(available_minutes=args.minutes, interrupted=args.interrupted)
    except (ValueError, ConstraintViolation) as error:
        print(f"出咗少少問題：{error}", file=sys.stderr)
        return 1

    if args.json:
        action, duration, tip = result.activity.variant(result.mode)
        print(
            json.dumps(
                {
                    "id": result.activity.id,
                    "category": result.category.value,
                    "mode": result.mode,
                    "action": action,
                    "duration": duration,
                    "tip": tip,
                    "affirmation": result.affirmation,
                    "char_count": result.char_count,
                    "text": result.text,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
