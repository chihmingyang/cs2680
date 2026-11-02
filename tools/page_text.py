#!/usr/bin/env python3
"""Print a lecture page as plain text, so reading it does not cost the whole HTML (read-only).

Usage:
  python3 -I tools/page_text.py docs/lXX.html              # the whole article
  python3 -I tools/page_text.py docs/lXX.html s-ideas      # one section: s-arch, s-ideas, s-discuss, s-try, wrap
  python3 -I tools/page_text.py docs/lXX.html ids          # every id on the page, one per line

Figures print as [FIG: aria-label] and [caption: …], so you can see what a figure says without its SVG.
Headings, bold sub-headings and anchors keep their id as {#id}; links show their target as (→target).
"""
import html
import re
import sys
from pathlib import Path


def section(s, sid):
    a = s.index(f'id="{sid}"')
    a = s.rfind("<section", 0, a)
    b = s.index("</section>", a)
    return s[a:b]


def to_text(h):
    h = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", "", h, flags=re.S)
    h = re.sub(r'<svg\b[^>]*aria-label="([^"]*)"[^>]*>.*?</svg>', r"\n[FIG: \1]\n", h, flags=re.S)
    h = re.sub(r"<svg\b.*?</svg>", "\n[FIG]\n", h, flags=re.S)
    h = re.sub(r"<figcaption>(.*?)</figcaption>", r"\n[caption: \1]\n", h, flags=re.S)
    h = re.sub(r'<span class="anchor" id="([^"]+)"></span>', r"{#\1} ", h)
    h = re.sub(r'<(h[1-6]|p|div|li|dt|details|section)\b[^>]*\sid="([^"]+)"[^>]*>', r"\n{#\2} ", h)
    h = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', lambda m: f"{m.group(2)}(→{m.group(1)})" if not m.group(1).startswith("http") else f"{m.group(2)}({m.group(1)})", h, flags=re.S)
    h = re.sub(r"</?(?:b|strong)>", "**", h)
    h = re.sub(r"<(?:p|div|li|tr|h[1-6]|ul|ol|table|details|summary|figure|pre|section|header|nav|dt|dd)\b[^>]*>", "\n", h)
    h = re.sub(r"</(?:td|th)>", " | ", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h)
    h = re.sub(r"[ \t]+\n", "\n", h)
    return re.sub(r"\n{2,}", "\n", h).strip()


def main():
    page = Path(sys.argv[1])
    s = page.read_text(encoding="utf-8")
    what = sys.argv[2] if len(sys.argv) > 2 else None
    if what == "ids":
        print("\n".join(re.findall(r'\sid="([^"]+)"', s)))
    elif what:
        print(to_text(section(s, what)))
    else:
        print(to_text(s[s.index("<main"):s.index("</main>")]))


if __name__ == "__main__":
    main()
