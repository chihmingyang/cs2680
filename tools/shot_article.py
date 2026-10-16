#!/usr/bin/env python3
"""Screenshot an article page once for a visual check.

Usage: python3 -I shot_article.py site/lXX.html
Writes /home/claude/cs2680/shots/<name>-arch-light.png, -arch-dark.png (every
figure.diagram), -discuss.png (first discussion card, hints open) and
-phone.png; prints horizontal overflow at 1280px and 390px.
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
        for i, f in enumerate(pg.query_selector_all("figure.diagram"), 1):
            f.scroll_into_view_if_needed()
            path = out / f"{stem}-arch{i}-{scheme}.png"; f.screenshot(path=str(path)); paths.append(path)
        if scheme == "light":
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
print(f"desktop scrollWidth={dw} (should be 1280); phone scrollWidth={mw} (should be 390)")
for x in paths:
    print(x)
