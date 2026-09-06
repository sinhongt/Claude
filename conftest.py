"""放喺 repo 根目錄，令 pytest 由任何位置運行都揾到 micro_recovery 套件。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
