# 題庫：每一節的小測與整合題

2026-11-08 起，pilot 是 L6 第 1–4 章。同一批題有兩個用途：讀者讀完一節就做那一節的題；CI 的第 2 層（`WORKFLOW.md` J）拿它當 regression test。

## 為什麼這樣切

James 2026-11-07 提出：一章一題太少，基本觀念一題、重要觀念幾題。把內容拆成一節一節有連貫性的 knowledge section，學完一節就做那一節的題（unit test），讀完幾章再做把幾節合起來用的題（integration test）。

這樣切的價值在診斷：

| 結果 | 代表什麼 | 怎麼做 |
|---|---|---|
| unit 題錯 | 那一節沒教好，或被改壞了 | 改那一節 |
| unit 題都對、整合題錯 | 每一節都教了，但節和節之間怎麼接沒寫出來（2026-10-19 James 說的「卡」） | 補承接句，或在後一節點出它接的是哪一節 |
| 都對，James 還是說看不懂 | 題庫缺了這一題 | 補一題，像修完 bug 補一個 test |

## 資料放在哪裡

- 題庫在頁面裡：`</main>` 之後、`<script src="app.js">` 之前的 `<script type="application/json" id="quiz">`。頁面就是唯一來源，不另開檔案。
- 審查包（`review_pack.py`）和 `page_text.py` 都會去掉 `<script>`，所以作答的 agent 讀不到答案。
- `app.js` 讀它，在每一節的最後放一個收合的「小測」，在 `scope` 最後一章的最後放「整合題」。讀者寫的答案和「都答到／有漏」只存在自己的瀏覽器（localStorage `cs2680.quiz.<lXX>.<題號>.a`、`.v`）。
- `edit.js` 不讓 `.ks-quiz` 進入編輯；小測是 JS 產生的，網頁編輯存檔也不會把它寫進 HTML。

格式（L6 的節錄）：

```json
{
  "version": 1,
  "scope": ["i1", "i2", "i3", "i4"],
  "sections": [
    {"id": "k1", "from": "i1",   "title": "錯誤相乘：pⁿ"},
    {"id": "k2", "from": "i1-1", "title": "算式的兩個前提"}
  ],
  "unit": [
    {"id": "k1a", "ks": "k1", "kind": "recall", "q": "題目", "key": ["要點一", "要點二"]},
    {"id": "k1b", "ks": "k1", "kind": "apply",  "q": "換數字的題目", "key": ["…"]}
  ],
  "integration": [
    {"id": "x1", "ks": ["k1", "k4", "k8"], "q": "題目", "key": ["…"]}
  ]
}
```

- **節＝文章自己的小節。** 章首（從 `#iN` 到第一個小節）是一節，每個帶 id 的小節（`p#iN-M`，粗體 lead-in 那一段）各是一節。`from` 是起點的 id，一節到下一節的起點為止。不在 HTML 加新標記。
- 章首只有一句過場時（例如 L6 第 3 章），它和第一個小節併成一節：`from` 寫章的 id，不寫第一個小節的 id。
- `scope` 列出題庫涵蓋的章。每一章的開頭都要屬於某一節。

## 出題規則

- 每一節至少一題 unit。重要觀念 2–3 題，其中至少一題 `apply`：換數字或換情境，文章裡沒有現成的答案，只能用那一節講的機制推出來。只問文章寫過的句子，人和 agent 都能「找到那句」就答對，不代表懂。
- `key` 一個要點一句，數字寫出來。評分照要點逐條判斷，所以每個要點要能單獨判斷對錯。「任選兩種」這類寫成一個要點，並列出全部可以接受的答案。
- 整合題至少用到兩節，問的是節和節之間的接點。例如 L6 的 x1：第 2 章說每步檢查、第 3 章說每 10 步驗證一次最省，兩者怎麼並存。
- 題目從現在的文字出。這是 snapshot test：抓「原本教了、後來被改壞」。抓「本來就沒教到」是審查者和 James 讀頁面的工作，不混在一起。
- 數字用程式算過再寫。
- 改了小節的 id 或刪了小節，`quiz.py check` 會報錯（`verify.sh` 會跑）。改了某一節的內容，對應題目的 `key` 也要跟著改。

## 怎麼跑（CI 第 2 層，現在手動）

```bash
python3 -I tools/quiz.py exam docs/l06.html > notes/quiz/exam.md        # 作答包：讀者文字＋題目，沒有答案
# 開一個新的 subagent：只讀 exam.md，照它的規則作答，寫 notes/quiz/ans.json
python3 -I tools/quiz.py grade docs/l06.html notes/quiz/ans.json > notes/quiz/judge.md
# 再開一個新的 subagent：只讀 judge.md，寫 notes/quiz/verdicts.json（每個要點 1 或 0）
python3 -I tools/quiz.py report docs/l06.html notes/quiz/ans.json notes/quiz/verdicts.json
```

- **一題「過」＝兩個條件都成立。** 評分 agent 判斷每個要點都答到，而且作答者引用的文字真的寫了；程式判斷定位落在對的節：unit 題至少一個定位在它那一節，整合題在它列的每一節各至少一個。
- 定位的規則是把「你知道不算，文章寫了才算」變成機械檢查。第 1 章圖 4 也寫了「88%」，但 K4 的題要引用 K4 那一節，才算 K4 教到了。
- 作答和評分用兩個不同的 agent，都沒看過寫作過程，評分的也沒看過作答的推理。
- 只跑受影響的題：改了某一節，跑那一節的題、以它為前置的節的題、含它的整合題。Pilot 先全跑。
- `report` 給兩組以上的 answers／verdicts，就會列出各次結果不一致的題（雜訊）。

## Pilot 結果（2026-11-08，L6 第 1–4 章）

（跑完補上）
