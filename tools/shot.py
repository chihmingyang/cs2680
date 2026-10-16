#!/usr/bin/env python3
"""Screenshot a lecture page for one visual check.

Usage: python3 -I shot.py site/lXX.html
Writes to /home/claude/cs2680/shots/<name>-*.png and prints the paths:
  - every figure.diagram (desktop 1280px, light theme)
  - page top at phone width (390px, dark theme)
  - horizontal overflow check at both widths
Google Fonts are blocked offline, so text renders in fallback fonts.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

src = Path(sys.argv[1]).resolve()
out = Path(__file__).resolve().parent.parent / "shots"
out.mkdir(exist_ok=True)
stem = src.stem
paths = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 1000}, color_scheme="light")
    pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    pg.goto(src.as_uri())
    pg.evaluate("document.documentElement.style.scrollBehavior='auto'")
    pg.wait_for_timeout(300)
    figs = pg.query_selector_all("figure.diagram")
    for i, f in enumerate(figs, 1):
        f.scroll_into_view_if_needed()
        path = out / f"{stem}-diagram{i}.png"
        f.screenshot(path=str(path))
        paths.append(path)
    dw = pg.evaluate("document.documentElement.scrollWidth")
    ph = b.new_page(viewport={"width": 390, "height": 844}, color_scheme="dark", device_scale_factor=1)
    ph.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ph.goto(src.as_uri())
    ph.wait_for_timeout(300)
    path = out / f"{stem}-phone-top.png"
    ph.screenshot(path=str(path))
    paths.append(path)
    mw = ph.evaluate("document.documentElement.scrollWidth")
    b.close()
print(f"desktop scrollWidth={dw} (should be 1280); phone scrollWidth={mw} (should be 390)")
for x in paths:
    print(x)
