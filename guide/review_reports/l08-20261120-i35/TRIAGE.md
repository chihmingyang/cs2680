# L8 3.5〈hit rate〉自架那一段改寫的審查紀錄　2026-11-20　checklist v19

James 把這一段標成橘色，說「這段看不太懂」。改寫後只審這三個單位：`#i3 ¶20`、`#i3 code2 說明`、`#i3 code2 內容`。兩輪，報告在同一個資料夾。

| 定位 | 輪 | 判定 | 修法或理由 |
|---|---|---|---|
| ¶20 | 1 | fix | 「不要只看設定開了沒有」的設定指不出是哪一個（前五段講的設定都是 TTL）：改成「不要只看 prefix cache 開了沒有」，題庫三處同步。小標「hit rate:」和前面的「Hit rate:」同名（NIT）：小標是 James 自己改的，不動。 |
| code2 內容 | 1 | fix，一部分 needs-source | 分母「查過 cache 的 token 數」和前文 hit rate 的分母沒有接起來：正文加一句說兩個計數各數什麼，括號標「本文的理解：就是 request 送進來的 input token」。vLLM 文件只寫 number of queried tokens，原始碼這個環境讀不到，沒有查證；來源檔記了要看哪個檔案。 |
| ¶20、code2 | 2 | 通過 | 0 BLOCK、0 NIT。 |
