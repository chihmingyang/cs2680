#!/usr/bin/env python3
"""Normalize punctuation inside Chinese prose of CS2680 pages.

Usage: python3 -I punct.py FILE.html [FILE.html ...] [--dry]

Only text nodes are touched. Skipped: <pre>, <code>, <script>, <style>, <title>,
<kbd>, and any element whose class includes "orig", "en-title", "en", "tab",
"range", "eyebrow", "tm" (mono labels). A text node is processed only if it
contains at least one CJK character.

Rules inside a processed node:
  ASCII , ; : ? ! -> full-width when not followed by a space and not in
  digit:digit / digit,digit / "://" patterns.
  ASCII ( ... ) pairs -> full-width pair.
"""
import re
import sys
from pathlib import Path

CJK = re.compile(r"[㐀-鿿豈-﫿　-〿＀-￯]")
SKIP_TAGS = {"pre", "code", "script", "style", "title", "kbd"}
SKIP_CLASSES = {"orig", "en-title", "en", "tab", "range", "eyebrow", "dg-tm", "k"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "circle", "line", "rect", "polyline", "polygon"}
TOKEN = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)
FULL = {",": "，", ";": "；", ":": "：", "?": "？", "!": "！"}


def convert(text):
    if not CJK.search(text):
        return text
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        if ch in FULL:
            nxt = text[i + 1] if i + 1 < n else ""
            prv = text[i - 1] if i > 0 else ""
            if nxt in {" ", "\n", "\t"}:
                out.append(ch)
                continue
            if nxt == "" and not CJK.match(prv or " "):
                out.append(ch)
                continue
            if ch in ",:" and prv.isdigit() and nxt.isdigit():
                out.append(ch)
                continue
            if ch == ":" and nxt == "/":
                out.append(ch)
                continue
            out.append(FULL[ch])
        else:
            out.append(ch)
    s = "".join(out)
    # parentheses pairs (no nesting inside a text node)
    s = re.sub(r"\(([^()\n]*)\)", lambda m: "（" + m.group(1) + "）", s)
    return s


def process(html):
    parts = TOKEN.split(html)
    stack = []  # (tag, skip)
    changed = 0
    for idx, part in enumerate(parts):
        if not part:
            continue
        if part.startswith("<!--"):
            continue
        if part.startswith("<"):
            if "aria-label=" in part:
                fixed = re.sub(r'aria-label="([^"]*)"', lambda m: 'aria-label="' + convert(m.group(1)) + '"', part)
                if fixed != part:
                    parts[idx] = part = fixed
                    changed += 1
            m = re.match(r"<\s*(/)?\s*([a-zA-Z0-9-]+)", part)
            if not m:
                continue
            closing, tag = m.group(1), m.group(2).lower()
            if part.endswith("/>") or tag in VOID or tag.startswith("!"):
                continue
            if closing:
                # pop to matching tag
                for j in range(len(stack) - 1, -1, -1):
                    if stack[j][0] == tag:
                        del stack[j:]
                        break
            else:
                cls = re.search(r'class\s*=\s*"([^"]*)"', part)
                classes = set(cls.group(1).split()) if cls else set()
                skip = tag in SKIP_TAGS or bool(classes & SKIP_CLASSES)
                stack.append((tag, skip))
            continue
        if any(skip for _, skip in stack):
            continue
        new = convert(part)
        if new != part:
            parts[idx] = new
            changed += 1
    return "".join(parts), changed


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    for f in files:
        p = Path(f)
        html = p.read_text(encoding="utf-8")
        new, changed = process(html)
        if dry:
            print(f"{p.name}: {changed} text nodes would change")
        else:
            p.write_text(new, encoding="utf-8")
            print(f"{p.name}: {changed} text nodes normalized")


if __name__ == "__main__":
    main()
