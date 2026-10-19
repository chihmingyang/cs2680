#!/usr/bin/env python3
"""Remap slide page numbers in a lecture page to the current PDF's page index.

Usage:
  python3 -I fix_pages.py tools/pagemap/l02.json site/l02.html [more files] [--dry]
  python3 -I fix_pages.py tools/pagemap/l02.json site/l03.html --xref L2   # only "L2 p.N"
  python3 -I fix_pages.py tools/pagemap/l02.json content/l02-basic.html --no-guard  # fragments

Run each map once per file. The guard (data-pages-total must still equal old_pages)
stops a second run on a full page; fragments and --xref have no such marker, so
check `git diff` before running them again.

Why: the page numbers in an article must match the page counter of a PDF viewer,
because readers open the official PDF and go page by page, and every a.ref link
uses #page=N (the physical page index). If the course re-exports a PDF (hidden
slides removed, cover dropped), the old numbers drift. See STYLE_ARTICLE.md §10.

The map file (JSON):
  {"pdf": "2_agent_use_1.pdf", "pages": 53,
   "old_pages": 60,
   "map": {"2": 1, ...},          # old page -> new page; missing = no longer in the PDF
   "start": {"22": 18}}           # optional: a different target when the page starts a range

What changes (default mode):
  - href="...<pdf>#page=N"            -> new N (range-start mapping)
  - text "p.N", "p.N–M", "p.N-M"      -> new numbers; skipped when preceded by "L<k> "
                                         (a reference to another lecture)
  - data-pages-total="old_pages" and the 頁數 meta value -> pages
--xref Lk mode changes only "Lk p.N" text in another lecture's page.
A page that is gone maps to the nearest page that still exists (forward for a
range start, backward for a range end).
"""
import json
import re
import sys
from pathlib import Path

DASH = "–"


def load(path):
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    m = {int(k): int(v) for k, v in spec["map"].items()}
    start = {int(k): int(v) for k, v in spec.get("start", {}).items()}
    return spec, m, start


def mapper(m, start, old_max):
    def one(n, role):
        if role == "start" and n in start:
            return start[n]
        if n in m:
            return m[n]
        if role == "end":
            k = n
            while k > 0 and k not in m:
                k -= 1
            if k in m:
                return m[k]
        k = n
        while k <= old_max and k not in m:
            k += 1
        if k in m:
            return m[k]
        raise ValueError(f"page {n} has no mapping")
    return one


def fmt(a, b=None):
    if b is None or a == b:
        return f"p.{a}"
    return f"p.{a}{DASH}{b}"


TEXT_REF = re.compile(r"(?<![A-Za-z0-9/#.=])p\.(\d+)(?:\s*[–-]\s*(\d+))?")


def remap_text(s, one, only_lecture=None):
    def rep(mo):
        before = s[max(0, mo.start() - 4):mo.start()]
        xref = re.search(r"L(\d+)\s?$", before)
        if only_lecture is None and xref:
            return mo.group(0)            # another lecture's page: leave it
        if only_lecture is not None and not (xref and f"L{xref.group(1)}" == only_lecture):
            return mo.group(0)
        a = int(mo.group(1))
        if mo.group(2):
            b = int(mo.group(2))
            na, nb = one(a, "start"), one(b, "end")
            return fmt(na, nb)
        return fmt(one(a, "single"))
    return TEXT_REF.sub(rep, s)


def process(html, spec, one, only_lecture=None):
    pdf = re.escape(spec["pdf"])
    tokens = re.split(r"(<[^>]+>)", html)
    out = []
    changes = 0
    for t in tokens:
        if t.startswith("<"):
            if only_lecture is None:
                new = re.sub(rf'({pdf}#page=)(\d+)', lambda mo: mo.group(1) + str(one(int(mo.group(2)), "start")), t)
                new = new.replace(f'data-pages-total="{spec["old_pages"]}"', f'data-pages-total="{spec["pages"]}"')
            else:
                new = t
        else:
            new = remap_text(t, one, only_lecture)
        changes += new != t
        out.append(new)
    html = "".join(out)
    if only_lecture is None:
        html, n = re.subn(rf'(<span class="k">頁數</span>){spec["old_pages"]}(</li>)', rf'\g<1>{spec["pages"]}\2', html)
        changes += n
    return html, changes


def main():
    args = [a for a in sys.argv[1:] if a not in ("--dry", "--no-guard")]
    dry = "--dry" in sys.argv
    guard = "--no-guard" not in sys.argv
    only = None
    if "--xref" in args:
        i = args.index("--xref")
        only = args[i + 1]
        del args[i:i + 2]
    spec, m, start = load(args[0])
    one = mapper(m, start, spec["old_pages"])
    for f in args[1:]:
        p = Path(f)
        html = p.read_text(encoding="utf-8")
        if guard and only is None and f'data-pages-total="{spec["old_pages"]}"' not in html:
            # guard: running twice would shift every number again
            print(f"{p.name}: skipped, no data-pages-total=\"{spec['old_pages']}\" (already remapped?)")
            continue
        new, n = process(html, spec, one, only)
        bad = [int(x) for x in re.findall(rf'{re.escape(spec["pdf"])}#page=(\d+)', new) if not 1 <= int(x) <= spec["pages"]]
        print(f"{p.name}: {n} tokens changed" + (f"; OUT OF RANGE {bad}" if bad else ""))
        if not dry and new != html:
            p.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
