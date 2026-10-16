#!/usr/bin/env python3
"""Final audit across all lecture pages (read-only).

Checks per page:
  - internal links: lXX.html / index.html targets exist; #anchors exist in the page
  - every <svg> in a figure has role="img" and a non-empty aria-label
  - no literal colors inside svg (fill="#..", stroke="#..", style=...color)
  - marker ids unique across the whole site (avoid cross-page copy collisions)
  - render at 390px dark and 1280px light: no horizontal overflow, no page errors
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "site"
pages = sorted(SITE.glob("l0*.html"))
problems = []
marker_ids = {}

for p in pages:
    raw = p.read_text(encoding="utf-8")
    ids = set(re.findall(r'\sid="([^"]+)"', raw))
    for href in re.findall(r'href="([^"]+)"', raw):
        if href.startswith("#"):
            if href[1:] not in ids:
                problems.append(f"{p.name}: anchor {href} has no target")
        elif re.fullmatch(r"(l0\d|index|submissions)\.html", href):
            if not (SITE / href).exists():
                problems.append(f"{p.name}: link to missing {href}")
        elif href.endswith(".css") or href.startswith("http"):
            pass
        else:
            problems.append(f"{p.name}: unexpected href {href}")
    for svg in re.findall(r"<svg\b[^>]*>", raw):
        if 'role="img"' not in svg or not re.search(r'aria-label="[^"]{8,}"', svg):
            problems.append(f"{p.name}: svg without role/aria-label: {svg[:80]}")
    for body in re.findall(r"<svg\b.*?</svg>", raw, re.S):
        if re.search(r'(fill|stroke)="#|style="[^"]*(color|fill|stroke)', body):
            problems.append(f"{p.name}: literal color inside svg")
        if "<style" in body or "<script" in body:
            problems.append(f"{p.name}: style/script inside svg")
        for mid in re.findall(r'<marker[^>]*id="([^"]+)"', body):
            if mid in marker_ids and marker_ids[mid] != p.name:
                problems.append(f"marker id {mid} used in {marker_ids[mid]} and {p.name}")
            marker_ids[mid] = p.name

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for p in pages:
        for vw, scheme in [(390, "dark"), (1280, "light")]:
            errs = []
            pg = b.new_page(viewport={"width": vw, "height": 900}, color_scheme=scheme)
            pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
            pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
            pg.goto(p.resolve().as_uri())
            pg.wait_for_timeout(150)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            if sw > vw:
                problems.append(f"{p.name}: horizontal overflow at {vw}px ({sw})")
            if errs:
                problems.append(f"{p.name}: page error at {vw}px: {errs[0][:120]}")
            pg.close()
    b.close()

print(f"audited {len(pages)} pages, {len(marker_ids)} marker ids")
print("\n".join(problems) if problems else "NO PROBLEMS")
