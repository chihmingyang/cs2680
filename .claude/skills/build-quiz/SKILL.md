---
name: build-quiz
description: 替一堂建題庫（每一節的小測與整合題）時用：James 說「替 L7 出題」「每個觀念加 test」「把 L6 的題庫做法套到別堂」；或某一節的內容改了、要補題。先由沒看過題目的 agent 列出每一節教的觀念，再出題，開卷與閉卷都過才 push。
---

# 出題：先列觀念，再出題，開卷、閉卷都過才 push

規則以 `guide/QUIZ.md` 為準，這份 skill 是操作步驟，順序照 L6 實際做過的（2026-11-08～09，42 節、320 個觀念、258 題 unit、7 題整合）。核心是三件事：

1. **清單先於題目。** 每一節的 `points` 是 spec，由一個沒看過題目的 agent 列。先出題再補清單，清單會照著題目列，等於拿 test 當 spec（L6 舊題庫只測到 42% 的觀念，限制類只有 27%）。
2. **兩關。** 開卷：只用文章答得出來，而且引用落在那一節。閉卷：不給文章，答得出來的題要查原因，是線索就改。
3. **作答、評分、分類都用全新的 subagent**（general-purpose，不是 fork）。它們沒看過出題的過程，才測得到「讀者只靠文章答不答得出」。

中間檔都放 `notes/quiz/lXX/`（`notes/` 不 commit）。一個 session 只做一堂。

## 0. 開工前

- **這堂的可讀性審查要先做完、push 了**（`readability-review`）。題庫是現在文字的 snapshot。先出題再改文字，`points` 和 `key` 都會過時。
- `mkdir -p notes/quiz/lXX`。
- 讀 `guide/QUIZ.md` 的〈讀者自測優先〉〈出題規則〉〈觀念涵蓋〉三節。讀者自測優先（2026-11-11）：題目問含義，不問精確值和出處；那一類在觀念清單標 `evidence`、不出題，數字由 `tools/check_numbers.py` 對照 `guide/sources/lXX.md`（`verify.sh` 會跑）。

## 1. 切節：`init`

```bash
python3 -I tools/quiz.py init docs/lXX.html     # 每章的章首一節、每個小節（p#iN-M）一節，寫進頁面
python3 -I tools/quiz.py units docs/lXX.html    # 每個單位屬於哪一節，抽查切得對不對
```

`init` 只在頁面還沒有題庫時才動作。章首只有一句過場時，它會自動併進第一個小節。然後手動改頁面裡的 JSON：

- **標 `core`**：每章的主要主張標 `"core": true`，通常是章首那一節，或標題、tldr 寫到的那個主張。L6 是 10 章 9 個。重點節之後要出至少 4 題。
- **目錄、名詞註、「其他查閱」這種章**：留一節，刪掉其他節（刪掉的範圍就併進前一節），之後只出 1–2 題選擇題。L6 第 10 章就是這樣。
- **節太細**（一段、只講一件事）可以刪掉那一節的項目，讓它併進前一節。節的邊界只看 `from`，不在 HTML 加標記。
- 這時 `quiz.py check` 會報「沒有 unit 題」，是正常的。

## 2. 列觀念：全新的 subagent

```bash
python3 -I tools/quiz.py spec docs/lXX.html > notes/quiz/lXX/spec.md
wc -l notes/quiz/lXX/spec.md
```

- 超過約 350 行就分兩包，例如 `spec docs/lXX.html i1 i2 i3 i4 i5 > spec-1.md`、`… i6 i7 i8 i9 i10 > spec-2.md`，各開一個 agent。列觀念只問「這一節教了什麼」，所以不需要前文。
- 開一個 general-purpose 的 subagent。Prompt 是三段接起來：
  1. `.claude/skills/build-quiz/points-prompt.md` 全文。
  2. 一行：「清單包在 `/home/claude/cs2680/notes/quiz/lXX/spec.md`，用 Read 讀它。結果寫到 `/home/claude/cs2680/notes/quiz/lXX/points-1.json`。」
  3. 一行：「不要讀 repo 裡的其他檔案，不要上網查。」
- 併進頁面：`python3 -I tools/quiz.py merge docs/lXX.html notes/quiz/lXX/points-*.json`
- 抽查：`python3 -I tools/quiz.py coverage docs/lXX.html | less`。看兩件事：
  - 五種 type 的比例。L6 是主張 104、機制 78、前提 31、限制 68、誤解 39。限制、前提、誤解加起來不到三分之一，多半是只列了 happy case：把那幾節退回去重列。
  - 重點節的條數。L6 的重點節多半有 8–12 條。
  - 每節平均條數。超過約 8 條，多半是把表格、清單的每一格拆成一條。
- 第一版常常又太細、邊界類又太少。L7 的第一版有 554 條（第 6–9 章平均每節 12.4 條），邊界類只占 24–30%。用 SendMessage 退回**同一個 agent** 修一次就好，它手上還有那包文字：同一張表講同一個結論的格子併成一條，再逐段掃一次保留語和「不是…而是…」。修完是 350 條，邊界類 57–60%。

## 3. 出題

### 3a. Unit 題：一次 2–3 章，一章範圍一個 subagent

出題的人可以看文章，它是作者，不是讀者。可以用 fork（帶著上面切節的脈絡），也可以用 general-purpose 加 `writer-brief.md`。一堂約 250 題，全部在主線寫會塞爆 context，所以要分批。

```bash
python3 -I tools/quiz.py spec docs/lXX.html i1 i2 i3 > notes/quiz/lXX/spec-i1-i3.md
python3 -I tools/quiz.py coverage docs/lXX.html > notes/quiz/lXX/points.md      # 現在每一條都是「沒有題目」
```

每個 subagent 的 prompt：

1. `.claude/skills/build-quiz/writer-brief.md` 全文。
2. 一行：「你負責 `notes/quiz/lXX/spec-i1-i3.md` 裡的節。觀念清單在 `notes/quiz/lXX/points.md`，只看你負責的節。結果寫到 `notes/quiz/lXX/unit-i1-i3.json`。」

幾個 subagent 可以同時跑：它們各寫各的檔，都不改 `docs/`。跑完之後：

```bash
python3 -I tools/quiz.py merge docs/lXX.html notes/quiz/lXX/unit-*.json
python3 -I tools/quiz.py check docs/lXX.html
```

出題的 agent 會在 `_notes` 寫出文章本身的問題（L7 有 8 條是真的：摘要和正文對不上、表格兩列的判準不一致、圖說的例子歸錯格、數字四捨五入對不上）。小的直接改正文，再看有沒有觀念或題目引用到被改的那一句，一起改；大的記下來給 James。

`check` 的 FAIL 要清到零：沒有題目的觀念要補題，`covers` 指錯節要改，重點節題數不夠要補。`warn 正確選項明顯最長` 列出的題要全部改掉，閉卷第一個抓到的就是這個。補題寫成一個小 JSON（`{"unit": [...]}`），用 `merge` 併進去。題號已經存在的題會被換掉。

### 3b. 整合題：主線自己寫

Unit 題都併好了才寫。

- 放兩組：一組放在中間某一章後面（`"after": "i4"`），一組放在最後一個有內容的章後面。一組 3–4 題。
- 每題至少用兩節，問的是節和節的接點：前一章說 A、後一章說 B，兩者怎麼並存；前面的機制換到後面的情境還成不成立。
- `after` 之後的節不能用，`check` 會擋。
- `ks` 只列要點真的用到的節。評分要求作答者在 `ks` 的每一節都有引用；L7 第一次 7 題整合題有 3 題沒過，要點都答到了，只是 `ks` 多列了一節。
- 寫成 `{"integration": [...]}`，再 `merge`、`check`。

## 4. 開卷：作答 → 評分 → 報告

```bash
python3 -I tools/quiz.py exam docs/lXX.html > notes/quiz/lXX/exam.md
```

- **題目多就依章分批**：超過約 120 題，就分成 `exam docs/lXX.html i1 i2 i3 i4 i5 > exam-a.md` 和 `… i6 … i10 > exam-b.md`。每包都帶整頁文字，只有題目分開。
- 每包一個全新的 general-purpose subagent，prompt 是：「讀 `/home/claude/cs2680/notes/quiz/lXX/exam-a.md`，照它開頭的規則作答，只輸出 JSON，寫到 `/home/claude/cs2680/notes/quiz/lXX/ans-a.json`。不要讀 repo 裡的其他檔案，不要上網查。」
- 合併答案，再評分：

```bash
python3 -I -c 'import json,sys; d={"_issues":{}}; [ (d["_issues"].update(x.pop("_issues",{})), d.update(x)) for x in (json.load(open(f,encoding="utf-8")) for f in sys.argv[2:]) ]; json.dump(d,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)' notes/quiz/lXX/ans.json notes/quiz/lXX/ans-*.json
python3 -I tools/quiz.py grade docs/lXX.html notes/quiz/lXX/ans.json > notes/quiz/lXX/judge.md
```

- 再開一個全新的 subagent 評分：「讀 `…/judge.md`，照它開頭的規則評分，只輸出 JSON，寫到 `…/verdicts.json`。不要讀其他檔案。」它沒看過作答者的推理，只看答案和引用。
- `python3 -I tools/quiz.py report docs/lXX.html notes/quiz/lXX/ans.json notes/quiz/lXX/verdicts.json`

**先看 `_issues`，再看分數。** L6 的教訓是作答的 agent 最會抓爛題：兩個選項都對、選項說得比文章多、題目要的東西文章沒寫。沒過的題，多半是題目的毛病：

| 沒過的原因 | 怎麼做 |
|---|---|
| 定位落在別節（文章在別處也寫了） | 題目改成問這一節才有的東西；或這個觀念其實屬於別節，把題和觀念一起搬過去 |
| 要點要求題目沒問的東西、或文章沒寫的東西 | 刪那個要點 |
| 選了「文章沒寫」，文章真的沒寫 | 題目說得比文章多：改題目。如果是文章自己缺一步，記下來給 James，不在這裡改正文 |
| 文章本身前後不一致（L6 第 5 章與第 8 章） | 記下來給 James 決定 |

改過的題只重跑那幾題：`exam docs/lXX.html k3b k7c > exam-r2.md`，作答與評分照上面。評分包也要列同樣的題號（`grade docs/lXX.html ans-r2.json k3b k7c`），不列的話，這一輪沒重跑的開放題會全部算成沒作答。目標是全過。

開卷和閉卷互不依賴，第一次可以同時開跑；兩邊要改的題合在一起改，再一起重跑。

## 5. 閉卷：只抓線索

```bash
python3 -I tools/quiz.py closed docs/lXX.html > notes/quiz/lXX/closed.md
```

- 全新的 subagent：「讀 `…/closed.md`，照它開頭的規則作答，只輸出 JSON，寫到 `…/closed.json`。不要讀其他檔案，不要上網。」
- `python3 -I tools/quiz.py closedcheck docs/lXX.html notes/quiz/lXX/closed.json > notes/quiz/lXX/closedcheck.txt`
- 預期大部分選擇題閉卷也答得對。L6 新寫的 203 題答對 202 題、有把握 179 題。作答的 LLM 背景知識比讀者強，所以這一關**只抓線索，不要求答不出來**。
- 再開一個全新的 subagent 分類：prompt 是 `.claude/skills/build-quiz/classify-prompt.md` 全文，加一行「題目在 `…/closed.md`，要分類的題和閉卷理由在 `…/closedcheck.txt`。結果寫到 `…/classify.json`。」
- 照分類處理：

| 類別 | 怎麼做 |
|---|---|
| `compute`（題幹給齊數字） | 計算搬到 apply 題，選擇題改問文章量到什麼、主張什麼 |
| `option`（正確選項最長，或錯的選項不合理） | 選項改成等長、等具體、同句型；錯的選項換成說得通的誤解 |
| `leak`，洩漏的題在同一節 | 改題幹或選項；兩題其實考同一件事，就併成一題（`covers` 合併）或後一題改成 apply |
| `leak`，只在別節出現 | 標 `closed_ok` |
| `knowledge`、`reasoning` | 標 `"closed_ok": "常識或推理：一句理由"` |

- 改過的題：閉卷再跑一次（`closed docs/lXX.html <題號…>`），開卷也再跑一次（`exam … <題號…>`）。線索類最多改兩輪。兩輪後還有線索的，和同一節另一題併掉，或刪掉，再看 `check` 有沒有觀念因此沒人測。

## 6. 驗證、紀錄、push

```bash
bash tools/verify.sh lXX            # ALL OK
python3 -I tools/shot_article.py docs/lXX.html   # 看一章：每節後面有收合的小測、重點節有「重點」標籤、整合題在 after 那章後面
```

- `guide/QUIZ.md`〈各堂題庫〉表加一列，`guide/README.md` 題庫那一列更新現有的講次。
- `guide/CHANGELOG.md` 的 QUIZ.md 一節，最上面加一行。
- 照 `WORKFLOW.md` D push。commit 訊息例：「L7 題庫：54 節、410 個觀念、296 題 unit、7 題整合；開卷全過、閉卷線索類改兩輪」。

## 7. 回報 James

他讀回報，不讀題目。給一張表和三件事：

- 表：節數；觀念數，分五種 type；unit 題數（選擇／應用）；整合題數；開卷第一次過幾題、改完後過幾題；閉卷答對而且有把握的題數、改了幾題、標 `closed_ok` 幾題。
- 作答者指出的**文章本身**的問題，一條一行，他決定要不要改正文。
- 切節和 `core` 的判斷：哪幾節是重點、為什麼；哪幾章併成一節。
- 哪裡要他確認。

## 只改了某一節（維護）

1. 先改那一節的 `points`：多教了一件事就加一條，刪掉的就拿掉。
2. `quiz.py check` 會指出哪一條沒有題目，補題，`merge`。
3. 只重跑受影響的題：`exam docs/lXX.html k7`（那一節的題，加上用到它的整合題）；有改選擇題就再跑 `closed docs/lXX.html k7`。

## 中斷時

Subagent 撞到用量上限會中斷，但常常已經把結果檔寫出來了（L7 兩個列觀念的 agent 都是寫完檔才在回報時中斷）。先檢查結果檔完不完整，再決定要不要用 SendMessage 叫同一個 agent 接著做，不要直接重開一個。

## 成本（L6 的數字）

- 開卷作答一次約 10–11 萬 token、3–5 分鐘；評分約 10 萬 token。只出幾題時，作答包還是帶整頁文字，約 7–9 萬 token。
- 整堂第一次：列觀念 1–2 個 agent、出題 3–4 個、開卷作答 2 個加評分 1 個、閉卷作答與分類各 1 個，之後每輪只跑改過的題。
