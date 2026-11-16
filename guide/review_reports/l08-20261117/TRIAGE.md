# L8 第 3 章〈Hit rate 的帳〉2026-11-17：算式和表換成一張圖之後的審查（checklist v19）

James 2026-11-17 貼了〈Hit rate 的帳〉的算式和表：「這表我看不懂算數，明明是個易懂的小觀念，就是 cache read 很重要，你加了算數後反而看不懂了。」算式（C、h、r、w 四項）和 7 列 2 欄的表全部刪掉，換成一張圖（hit rate 95% 時，token 量 95：5，錢 60：40）。只審改過的 5 個單位，前面的章當上下文。事件存成測試題 `guide/review_cases/l08-i3-hitrate-formula.md`。

## 第一輪：4 BLOCK、2 NIT
兩個是刪字帶進來的：原段定義了 base input，刪掉之後它的第一次出現移到後面的圖說。
- `#i3-2` 第一段 R15（「input token」沒解釋）：fix，合併。Hit rate 的分母改用第 2 章定義過的 context，圖的列名跟著改。
- 圖 R1（「花的錢」含不含 output）：fix。列名改成「讀 context 的錢」，圖說加「output 另外算」。
- 結論段 R9（「每掉一個百分點帳單都看得出來」沒有數字）：fix，刪掉這一句；章首的預告改成「幾個百分點的 cache miss 佔多少錢」。
- 結論段 R3、R13（「不開 cache」「一般 input」「貴 25%」）：fix，補字（刪不掉：這是這一節第二個結論）。另起一段，定義 base input，寫出 1.25×。
- 單價圖的圖說 R15、R16（「同一個 token」對不上 output 和 cache read 兩端）：fix。問句改成「各種 token 的單價差多少」，寫出是哪兩根差 100 倍。
- NIT R11（四成要自己算）：不修，圖照比例畫，讀者不必算。NIT R7（batch 之後直接接單價圖）：不在這次改的範圍。

## 第二輪：0 BLOCK、0 NIT
審查者列的最難讀的一處照修：「Cache miss 還不是照原價收」有兩種讀法，改成「Cache miss 收的比原價還高」。
範圍外看到、照修：〈TTL 的帳〉的算式用了 r，那一段只定義 C、G、k；r 原本在〈Hit rate 的帳〉定義，這次刪掉了，所以在〈TTL 的帳〉補上 r 的定義。
