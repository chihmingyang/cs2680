---
name: answer-comments
description: 開工時 tools/comments.py list 有等回答的留言、或 James 說「回答留言」「看我的留言」時用。James 在站台頁面上選字留言（label comment 的 issue），這裡逐則回答；留言說看不懂的，答案要寫回文件，讓下一個讀者不必再問。改文件照平常的審查與發布，最後在每一串回覆並標成 answered。
---

# 回答站台留言

James 讀頁面時選一段文字按「留言」（`docs/edit.js`），留言存成 label `comment` 的 issue，裡面有檔名、錨點、引用的原文。留言不會馬上有人回答：下一個 session 用這份 skill 一次處理。

**留言說看不懂，就是文件寫壞了。** 只在 issue 裡回答，下一個成員讀到同一段還是看不懂。所以答案的去處是文件，issue 裡的回覆是告訴他改了哪裡。

## 1. 讀留言

```bash
cd /home/claude/cs2680 && git pull --rebase
python3 -I tools/comments.py list          # 等 Claude 的串，連同整串對話；沒有就結束
python3 -I tools/page_text.py docs/l03.html s-ideas | grep -n -A15 '{#i2-4}'   # 錨點附近的原文
```

一串裡 James 後來又回覆（「還是不懂第二句」），以最後一則為準，前面的回答也要讀，不要重複一樣的說法。

## 2. 每一則歸類

| 類 | 留言長什麼樣 | 怎麼處理 |
|---|---|---|
| A 看不懂 | 「這是什麼」「為什麼」「這句在說什麼」，問的是這一頁本來就該講清楚的事 | 照 `rewrite-with-example` 改文件，答案寫進正文。再照 `learn-from-edit` 第 3 步問：流程哪一步該抓到？審查者漏了就存一題 `guide/review_cases/` |
| B 延伸問題 | 「那 X 呢」「跟 Y 比呢」，超出這一頁的範圍 | 在回覆裡答。其他成員也會想問、而且答案能從第一性原理講清楚的，才寫進文件（正文一段或本文延伸） |
| C 改稿指示 | 「這段刪掉」「這裡要一張圖」「換個例子」 | 照做 |
| D 事實質疑 | 「這數字對嗎」「真的是這樣？」 | 查原始來源；站台外的評論照 `fact-check-extension` |
| E 要他決定 | 牽涉規則、章的順序、刪一整節 | 不改。回覆寫兩三個選項和各自的代價，等他回 |

一則可以同時是 A 和 C。分不清 A 還是 B 時當 A：寧可文件多講清楚一點。

## 3. 改文件、發布

同一堂的留言一起改，改完照 WORKFLOW C：`bash tools/verify.sh lXX`、改過的單位跑可讀性審查（I）、要的話標紅字（I2）、push（D）。新規則照 C 先問他（放在回覆裡，類 E）。

## 4. 回覆每一串

push 之後才回覆，連結才看得到新文字（Pages 約 1–2 分鐘）。

```bash
cat > notes/reply-110.md <<'MD'
「fork」在這裡是複製一份對話給 subagent：它拿到主對話到目前為止的全部內容，從那裡接著跑。

文件改了：[第 2 章〈Subagent〉](https://chihmingyang.github.io/cs2680/l03.html#i2-4) 第一次出現 fork 的地方補了這句定義和一個例子。
MD
python3 -I tools/comments.py reply 110 notes/reply-110.md
```

- 先一兩句直接回答，再一行「文件改了：連結＋改了什麼」或「文件沒改：理由」。不貼改過的全文，他點連結看。
- 不關 issue。James 看完按「解決」就是關閉；他回覆，那一串會拿掉 `answered`，下一次 `list` 再出現。

## 5. 回覆 James

先講這批留言看出的規律（例如「三則都是名詞第一次出現沒定義」，以及流程補了什麼），再一則一行：

```
#110 L3 #i2-4 fork 是什麼 → A：補定義，審查者漏了，存成測試題
#111 L8 #i3-2 batch 跟 cache 誰先 → B：只回答，不進文件（理由）
#112 L6b 這段刪掉 → C：刪了
```

要他決定的（類 E）放最後。
