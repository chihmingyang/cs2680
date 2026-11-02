#!/usr/bin/env python3
"""Keep links working when a lecture's anchors change (v7 重組, 2026-11-03).

anchor-map.json is a flat object {"old id": "new id"} for one lecture.

  python3 -I tools/anchor_map.py list docs/lXX.html
      Prints the ids of this page that the map has to cover (i*, t*, x*, d*, n-*, s-arch), and which other
      pages link to each one right now.
  python3 -I tools/anchor_map.py check docs/lXX.html notes/lXX/old.html notes/lXX/anchor-map.json
      Every coverable id of the old page must be a key, and every value must exist in the new page.
  python3 -I tools/anchor_map.py apply lXX notes/lXX/anchor-map.json docs/index.html docs/l01.html …
      Rewrites href="lXX.html#old" to the new id in the given pages, in one pass (no chaining).
"""
import json
import re
import sys
from pathlib import Path

COVER = re.compile(r"(i\d+(-\d+)?|t\d+|x\d+|d\d+|n-[\w-]+|s-arch)$")


def ids(path):
    return re.findall(r'\sid="([^"]+)"', Path(path).read_text(encoding="utf-8"))


def main():
    mode = sys.argv[1]
    if mode == "list":
        page = Path(sys.argv[2])
        site = page.parent
        links = {}
        for q in sorted(site.glob("*.html")):
            if q.name == page.name:
                continue
            for frag in re.findall(rf'href="{page.name}#([\w-]+)"', q.read_text(encoding="utf-8")):
                links.setdefault(frag, []).append(q.name)
        for i in ids(page):
            if COVER.fullmatch(i):
                print(i, " ".join(links.get(i, [])))
    elif mode == "check":
        new, old, m = sys.argv[2], sys.argv[3], json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
        have = set(ids(new))
        bad = [f"not covered: {i}" for i in ids(old) if COVER.fullmatch(i) and i not in m]
        bad += [f"{k} -> {v}: no such id in the new page" for k, v in m.items() if v not in have]
        print("\n".join(bad) if bad else f"OK ({len(m)} anchors)")
        sys.exit(1 if bad else 0)
    elif mode == "apply":
        key, m = sys.argv[2], json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
        for f in sys.argv[4:]:
            p = Path(f)
            s = p.read_text(encoding="utf-8")
            n = 0

            def sub(g):
                nonlocal n
                new = m.get(g.group(1), g.group(1))
                n += new != g.group(1)
                return f'href="{key}.html#{new}"'

            t = re.sub(rf'href="{key}\.html#([\w-]+)"', sub, s)
            if t != s:
                p.write_text(t, encoding="utf-8")
            print(f"{p.name}: {n} links changed")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
