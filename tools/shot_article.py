#!/usr/bin/env python3
"""Screenshot an article page once for a visual check.

Usage: python3 -I shot_article.py docs/lXX.html
Writes shots/<name>-arch<i>-light.png and -dark.png (every figure.diagram in #s-arch and #s-ideas,
opening a collapsed 深入 block if needed), -basic.png (first basic question, answer open), -discuss.png
(first 進階 card, all details open) and -phone.png into the folder next to tools/;
prints horizontal overflow at 1280px and 390px. Open each PNG with Read once.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

src = Path(sys.argv[1]).resolve()
out = Path(__file__).resolve().parent.parent / "shots"; out.mkdir(exist_ok=True)
stem = src.stem
paths = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ("light", "dark"):
        pg = b.new_page(viewport={"width": 1280, "height": 1000}, color_scheme=scheme)
        pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        pg.goto(src.as_uri()); pg.wait_for_timeout(300)
        for i, f in enumerate(pg.query_selector_all("#s-arch figure.diagram, #s-ideas figure.diagram"), 1):
            # a figure inside a collapsed 深入 block is invisible until its <details> are open
            f.evaluate("el => { for (let d = el.closest('details'); d; d = d.parentElement.closest('details')) d.open = true; }")
            f.scroll_into_view_if_needed()
            path = out / f"{stem}-arch{i}-{scheme}.png"; f.screenshot(path=str(path)); paths.append(path)
        if scheme == "light":
            bq = pg.query_selector(".bq")
            if bq:
                for s in bq.query_selector_all("summary"):
                    s.click()
                bq.scroll_into_view_if_needed(); pg.wait_for_timeout(150)
                path = out / f"{stem}-basic.png"; bq.screenshot(path=str(path)); paths.append(path)
            tab = pg.query_selector("#tab-adv")
            if tab:
                tab.click(); pg.wait_for_timeout(100)
            card = pg.query_selector(".dq")
            if card:
                for s in card.query_selector_all("summary"):
                    s.click()
                card.scroll_into_view_if_needed(); pg.wait_for_timeout(150)
                path = out / f"{stem}-discuss.png"; card.screenshot(path=str(path)); paths.append(path)
            dw = pg.evaluate("document.documentElement.scrollWidth")
        pg.close()
    ph = b.new_page(viewport={"width": 390, "height": 844}, color_scheme="dark")
    ph.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ph.goto(src.as_uri()); ph.wait_for_timeout(300)
    path = out / f"{stem}-phone.png"; ph.screenshot(path=str(path)); paths.append(path)
    mw = ph.evaluate("document.documentElement.scrollWidth")
    b.close()
print(f"desktop scrollWidth={dw} (must not exceed 1280); phone scrollWidth={mw} (must not exceed 390)")
for x in paths:
    print(x)
