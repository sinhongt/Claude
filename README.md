# Claude

小型 Python 練習 repo。

## 微休息（micro-recovery）提示系統

畀長時間做密集文書工作嘅人用。每次被觸發（定時提醒、cron、App）就輸出一個
3-5 分鐘、坐喺辦公桌前就做得嘅恢復動作，並且喺**視覺休息／身體伸展／呼吸放鬆**
三個類別之間輪替，唔會連續兩次出同一類。

純 stdlib，冇任何 runtime 依賴（測試先需要 pytest）。

### 用法

```bash
python -m micro_recovery                 # 預設：3-5 分鐘完整版
python -m micro_recovery --minutes 1     # 只得 1-2 分鐘 → 自動出壓縮版
python -m micro_recovery --interrupted   # 上次做到中途被打斷 → 先加一句簡短肯定
python -m micro_recovery --json          # 畀 App 解析嘅格式
python -m micro_recovery --seed 7        # 固定隨機種子，方便重現
```

輸出樣本：

```
【今日微休息】
▸ 動作：可以望向窗外嘅綠色或天空，數20個呼吸，期間唔睇任何螢幕
▸ 時間：4分鐘
▸ 提示：望啲遠而又唔規則嘅景，腦袋自然放鬆，唔使刻意集中
```

當作程式庫用：

```python
from micro_recovery import MicroRecoveryEngine

engine = MicroRecoveryEngine()
result = engine.trigger(available_minutes=3, interrupted=False)
print(result.category.value, result.mode, result.char_count)
print(result.text)
```

掛落 cron，例如每 90 分鐘提一次：

```cron
0 */1 * * * /usr/bin/python3 -m micro_recovery >> ~/micro_recovery.log
```

### 狀態檔

輪替狀態預設寫喺 `~/.micro_recovery/state.json`，可以用 `--state` 或環境變數
`MICRO_RECOVERY_STATE` 覆寫。因為每次提醒通常都係一個新 process，狀態一定要
寫落盤，「唔連續兩次同類別」先至守得住。

檔案壞咗、格式唔識，引擎唔會拋錯，只會由頭開始輪替——提醒工具唔應該因為
一個快取檔而出唔到聲。

### 設計要點

約束條件係**可執行程式碼**，唔係註釋：

- `validator.py` — 擋住命令式語氣（「你應該」「你必須」…）、負面後果語言
  （「浪費」「唔夠」…）、醫學術語（「睫狀肌」「副交感」…），要求動作句有
  邀請式標記（「不妨」「可以」…），並檢查字數。
- `selector.py` — 兩層 LRU：先排除上次用過嘅類別，再喺類別內揀最久未出現
  嘅動作。純函式，rng 由外面注入，所以完全可重現。
- `engine.py` — `resolve_mode()`：冇講時間 → 完整版；1-2 分鐘 → 壓縮版；
  超過 5 分鐘 → 仍然只出核心 3-5 分鐘內容，唔會為咗填時間而加長。
- `library.py` — 三類別各 6 個動作。壓縮版係獨立寫嘅最低門檻動作，唔係完整版
  嘅縮寫。

字數定義：`validator.count_chars()` 排除 `【】▸：`、標題同空白，只計實際內容。
完整版 60-90 字（規格要求）；壓縮版 30-60 字（規格明言 1-2 分鐘唔好強行塞滿，
所以下限下調）。

### 加新動作

喺 `micro_recovery/library.py` 嘅 `ACTIVITIES` 加一個 `Activity`，完整版同壓縮版
都要填。跑測試就會即刻話你知有冇違反語氣、術語或字數約束——`tests/test_library.py`
會掃全庫 36 個渲染（18 個動作 × 2 個模式）。

### LLM 版本

`prompts/micro_recovery.system.md` 係同一套規格嘅 system prompt，用嚟直接餵入
對話模型或 App。模型冇記憶，所以呼叫方要每次帶入「上次類別／可用時間／
是否被打斷」。

### 測試

```bash
python -m pytest tests -q
```

## 簡單計算機

`calculator.py` — 加減法嘅互動式 CLI。

```bash
python calculator.py
```
