# 審查者的測試題

一個檔一個事件：James 說看不懂、讀不順、或讀錯的一段，取修改前的版本。
用途是量審查者：這些地方，審查者能不能在 James 之前擋下來。格式與指令寫在 `tools/review_eval.py` 開頭，規則在 `guide/REVIEW_READABILITY.md`〈審查者的測試題〉。

- 新事件 → 加一個檔。`ref` 填還留著原文的那個 commit，`match` 填原文裡幾個字。
- `in_prompt: yes` 表示這段原文被 `reviewer-prompt.md` 引用當例子；它被抓到不算數，分開計。
- 原文不用貼進來，工具從 git 取。
