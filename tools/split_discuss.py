#!/usr/bin/env python3
"""Split §5 of an article page into 基礎 / 進階 tabs.

Usage: python3 -I split_discuss.py site/lXX.html content/lXX-basic.html

- content/lXX-basic.html holds <div class="qset" id="qset-basic">…</div>.
- The page's existing copyrow + textarea + ol.qlist become the 進階 set.
Idempotent: a page that already has .qtabs is left alone (exit 1).
"""
import re
import sys
from pathlib import Path

page = Path(sys.argv[1])
basic = Path(sys.argv[2]).read_text(encoding="utf-8").rstrip("\n")
s = page.read_text(encoding="utf-8")
if 'class="qtabs"' in s:
    print(page.name, "already split"); sys.exit(1)

lec = re.search(r'data-lecture="l(\d+)"', s).group(1).lstrip("0")

# 1. lede in §5 header
old_lede = re.search(r'(<section class="part" id="s-discuss">.*?<p class="lede">)(.*?)(</p>)', s, re.S)
assert old_lede, "no lede in s-discuss"
adv_lede = old_lede.group(2)
new_lede = "分兩組。基礎題在看 slides 之前讀，帶著問題看，答案都在 slides 裡。進階題在讀完文章後回答，讀書會前發給大家。"
s = s[:old_lede.start(2)] + new_lede + s[old_lede.end(2):]

# 2. locate copyrow … </ol> of the advanced set
m = re.search(r'(\n[ \t]*)<div class="copyrow">.*?</ol>\n', s[old_lede.start():], re.S)
assert m, "no copyrow/ol in s-discuss"
start = old_lede.start() + m.start()
end = old_lede.start() + m.end()
indent = m.group(1).lstrip("\n")
block = s[start:end]

# remove the textarea from inside the block; keep one after both sets
ta = re.search(r'[ \t]*<textarea class="copybox"[^>]*></textarea>\n', block)
assert ta, "no textarea"
textarea = ta.group(0).strip()
block = block[:ta.start()] + block[ta.end():]

# button attributes
block = re.sub(r'<button type="button" class="copybtn" id="copy-q" data-title="CS2680 L\d+ 讀書會討論題：',
               f'<button type="button" class="copybtn" data-copy="adv" data-title="CS2680 L{lec} 進階題（讀書會討論）：', block)
assert 'data-copy="adv"' in block, "button not rewritten"
block = block.replace(">複製討論題</button>", ">複製進階題</button>")

tabs = f'''
{indent}<div class="qtabs" role="tablist" aria-label="題目分組">
{indent}  <button type="button" class="qtab" role="tab" id="tab-basic" aria-controls="qset-basic" aria-selected="true">基礎<span>帶著問題看 slides</span></button>
{indent}  <button type="button" class="qtab" role="tab" id="tab-adv" aria-controls="qset-adv" aria-selected="false">進階<span>讀書會討論</span></button>
{indent}</div>
'''
adv_open = f'{indent}<div class="qset" id="qset-adv" role="tabpanel" aria-labelledby="tab-adv" hidden>\n{indent}  <p class="qset-lede">{adv_lede}</p>'
adv_body = "\n".join(("  " + ln if ln.strip() else ln) for ln in block.strip("\n").split("\n"))
adv_close = f'\n{indent}</div>\n{indent}{textarea}\n'
new_block = tabs + basic + "\n" + adv_open + "\n" + adv_body + adv_close
s = s[:start] + new_block + s[end:]

# 3. readhow
s = re.sub(r'<p class="readhow">.*?</p>',
           '<p class="readhow">建議順序：先讀第 5 段的基礎題，帶著問題自己一頁一頁看完 slides；再回來讀這篇。讀書會前用第 5 段的進階題。</p>',
           s, count=1, flags=re.S)
# 4. TOC label
s = s.replace('<li><a href="#s-discuss">5 問題討論<span>讀書會</span></a></li>',
              '<li><a href="#s-discuss">5 問題討論<span>基礎／進階</span></a></li>')
page.write_text(s, encoding="utf-8")
print(page.name, "split OK")
