#!/usr/bin/env python3
"""Which chapters has the readability review covered, and with which version of the checklist?

A review passes text only against the checklist of that day. When the checklist grows (R9, R10 …)
or a chapter is edited afterwards, the old pass says nothing about the new state. This script keeps
one line per reviewed group (tldr or chapter) in guide/review_log.tsv and compares it with the page:

  ok        reviewed with the current checklist, text unchanged since
  舊規則    text unchanged, but reviewed with an older checklist version
  改過      text changed after the review (any checklist)
  沒審過    no record

The checklist version is the line "Checklist 版本：N" in guide/REVIEW_READABILITY.md.

Usage:
  python3 -I tools/review_status.py status [l06b ...]      # per group for these pages; with no page: one count line per page
  python3 -I tools/review_status.py status l06b --note     # one line, only if something is not ok (verify.sh)
  python3 -I tools/review_status.py stale l06b             # group ids that are not ok, for review_pack.py --chapter
  python3 -I tools/review_status.py mark l06b i2 i3        # record: these groups pass the CURRENT checklist now
  python3 -I tools/review_status.py mark l06b              # … every group of the page
  python3 -I tools/review_status.py mark l06 --at c80866a --checklist 10 --date 2026-11-07 [groups]
                                                           # backfill: the text as of that commit was reviewed with v10

Run `mark` after the second review round has no BLOCK left (WORKFLOW I step 5). Only `mark` writes
(guide/review_log.tsv); everything else is read-only.
"""
import argparse
import datetime
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_pack import chapters, parse, tldr_of, units_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "guide" / "review_log.tsv"
HEADER = "# page\tgroup\tchecklist\tdate\ttext-hash\tnote\n"


def checklist_version():
    m = re.search(r"Checklist 版本：(\d+)", (ROOT / "guide" / "REVIEW_READABILITY.md").read_text(encoding="utf-8"))
    if not m:
        sys.exit("guide/REVIEW_READABILITY.md has no 'Checklist 版本：N' line")
    return int(m.group(1))


def groups_of(html):
    """{group id: hash of its reader-visible text}, in reading order."""
    root = parse(html)
    out = {}
    t = tldr_of(root)
    if t is not None:
        out["tldr"] = t
    for c in chapters(root):
        out[c.attrs.get("id", "?")] = c
    return {k: hashlib.sha1("\n".join(tx for _, tx in units_of(n, "")).encode()).hexdigest()[:12]
            for k, n in out.items()}


def read_log():
    rows = {}
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                p = line.split("\t")
                rows[(p[0], p[1])] = p
    return rows


def write_log(rows):
    LOG.write_text(HEADER + "".join("\t".join(r) + "\n" for _, r in sorted(rows.items())), encoding="utf-8")


def pages(names):
    if names:
        return names
    return sorted(p.stem for p in (ROOT / "docs").glob("l[0-9][0-9]*.html") if re.fullmatch(r"l\d\d[a-z]?", p.stem))


def state(page, cur, rows, ver):
    out = {}
    for g, h in cur.items():
        r = rows.get((page, g))
        if r is None:
            out[g] = ("沒審過", "")
        elif r[4] != h:
            out[g] = ("改過", f"v{r[2]} {r[3]}")
        elif int(r[2]) < ver:
            out[g] = ("舊規則", f"v{r[2]} {r[3]}")
        else:
            out[g] = ("ok", f"v{r[2]} {r[3]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["status", "stale", "mark"])
    ap.add_argument("names", nargs="*")
    ap.add_argument("--note", action="store_true")
    ap.add_argument("--at")
    ap.add_argument("--checklist", type=int)
    ap.add_argument("--date")
    ap.add_argument("--why", default="")
    a = ap.parse_args()
    ver = checklist_version()
    rows = read_log()

    if a.cmd == "mark":
        if not a.names:
            sys.exit("mark needs a page: mark l06b [groups]")
        page, want = a.names[0], a.names[1:]
        if a.at:
            r = subprocess.run(["git", "show", f"{a.at}:docs/{page}.html"], capture_output=True, text=True, cwd=ROOT)
            if r.returncode != 0:
                sys.exit(r.stderr.strip())
            html = r.stdout
        else:
            html = (ROOT / "docs" / f"{page}.html").read_text(encoding="utf-8")
        cur = groups_of(html)
        bad = [g for g in want if g not in cur]
        if bad:
            sys.exit(f"{page} has no group {' '.join(bad)} (has: {' '.join(cur)})")
        date = a.date or datetime.date.today().isoformat()
        for g in want or cur:
            rows[(page, g)] = [page, g, str(a.checklist or ver), date, cur[g], a.why]
        write_log(rows)
        print(f"marked {page}: {' '.join(want or cur)}　checklist v{a.checklist or ver}　{date}")
        return

    for page in pages(a.names):
        cur = groups_of((ROOT / "docs" / f"{page}.html").read_text(encoding="utf-8"))
        st = state(page, cur, rows, ver)
        by = {}
        for g, (s, _) in st.items():
            by.setdefault(s, []).append(g)
        if a.cmd == "stale":
            print(" ".join(g for g, (s, _) in st.items() if s != "ok"))
        elif a.note:
            if set(by) != {"ok"}:
                parts = [f"{s}：{'、'.join(by[s])}" for s in ("改過", "沒審過", "舊規則") if s in by]
                print(f"note review {page}（checklist v{ver}）　" + "　".join(parts)
                      + f"　→ python3 -I tools/review_status.py stale {page}")
        else:
            print(f"{page}　checklist v{ver}　" + "　".join(f"{s} {len(by[s])}" for s in ("ok", "舊規則", "改過", "沒審過") if s in by))
            for g, (s, info) in st.items():
                if s != "ok" and a.names:
                    print(f"  {g}\t{s}\t{info}")


if __name__ == "__main__":
    main()
