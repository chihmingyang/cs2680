#!/usr/bin/env python3
"""Test the readability REVIEWER against passages James actually could not read.

Each case in guide/review_cases/*.md is one incident: a page at the commit BEFORE the fix, the
chapter it sits in, and a few words that identify the unit(s) James complained about. A fresh
reviewer gets the same pack a real review would get (the chapter, with everything before it as
context). The case is "caught" when the reviewer marks at least one of those units BLOCK.

The number this prints, recall, is "of the places James complained about, how many would the
reviewer have stopped first". review_noise.py measures whether the reviewer is stable; this
measures whether it is right. Run it after every change to reviewer-prompt.md or the checklist.

Usage:
  python3 -I tools/review_eval.py list                 # the cases, with their units at that commit
  python3 -I tools/review_eval.py pack [id ...]        # write notes/review/cases/<id>-pack.md (all cases if no id)
  python3 -I tools/review_eval.py score                # read notes/review/cases/<id>-report.md, print recall

Between pack and score: one fresh reviewer (subagent) per case, prompt = reviewer-prompt.md + the
pack path + the report path notes/review/cases/<id>-report.md (readability-review skill, step 2).
Do not tell the reviewer which unit is the incident.

Cases marked `in_prompt: yes` are quoted in reviewer-prompt.md as examples, so catching them proves
little; recall is printed for all cases and for the held-out ones (in_prompt: no) apart.

Case file format (guide/review_cases/<id>.md):
  ---
  page: docs/l06b.html
  ref: 75ec560dd5            # commit that still has the unreadable text
  chapter: i2                # or tldr
  match: 歸納是風險最高的寫入 | 少了上面 snippet     # substrings; each picks the unit(s) containing it
  rules: R10 R15 R16         # which checklist items should fire (for the report, not for scoring)
  in_prompt: no
  date: 2026-11-11
  ---
  free text: what James said, why the review missed it
Writes only under notes/review/cases/ (not committed).
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_pack import pack, parse  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "guide" / "review_cases"
OUT = ROOT / "notes" / "review" / "cases"
FLAG = re.compile(r"^(BLOCK|NIT) \[([^\]]+)\]")


def norm(loc):
    return re.sub(r"\s+", " ", re.sub(r"\s*‹[^›]*›", "", loc)).strip()


def load(path):
    head, _, body = path.read_text(encoding="utf-8").partition("\n---\n")
    meta = {}
    for line in head.splitlines():
        m = re.match(r"(\w+):\s*(.*?)\s*(?:#.*)?$", line)
        if m:
            meta[m.group(1)] = m.group(2)
    meta["id"] = path.stem
    meta["body"] = body.strip()
    meta["match"] = [s.strip() for s in meta.get("match", "").split("|") if s.strip()]
    return meta


def cases(ids=()):
    out = [load(p) for p in sorted(CASES.glob("*.md")) if p.name != "README.md"]
    if ids:
        out = [c for c in out if c["id"] in ids]
        missing = set(ids) - {c["id"] for c in out}
        if missing:
            sys.exit(f"no such case: {' '.join(sorted(missing))}")
    return out


def old_html(c):
    spec = f"{c['ref']}:{c['page']}"
    r = subprocess.run(["git", "show", spec], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:  # shallow clone (WORKFLOW A clones with --depth 1): fetch just that commit
        subprocess.run(["git", "fetch", "--depth", "1", "origin", c["ref"]], capture_output=True, cwd=ROOT)
        r = subprocess.run(["git", "show", spec], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"{c['id']}: git show {spec} failed: {r.stderr.strip()}")
    return r.stdout


def build(c):
    """(groups, targets): the review pack of the case, and the locators of the incident units."""
    groups = pack(parse(old_html(c)), {c["chapter"]}, (), c["chapter"] != "tldr")
    targets = []
    for _, _, units, under_review in groups:
        if under_review:
            targets += [(loc, tx) for loc, tx in units if any(s in tx for s in c["match"])]
    if not targets:
        sys.exit(f"{c['id']}: no unit in {c['chapter']} at {c['ref']} contains {c['match']}")
    return groups, targets


def render(c, groups):
    n = sum(len(u) for _, _, u, r in groups if r)
    ctx = sum(len(u) for _, _, u, r in groups if not r)
    lines = [f"# 審查包：{Path(c['page']).name}　審 1 組　{n} 個單位" + (f"　另有上下文 {ctx} 個單位" if ctx else ""),
             "# 每一行是一個單位：[定位] 文字。表格格子帶欄名 ‹…› 與列名。"]
    if ctx:
        lines.append("# 標「上下文」的組是讀者在審查範圍之前讀過的文字：讀，但不審。審查範圍之後的文字不在這份審查包裡。")
    for title, loc, units, under_review in groups:
        lines.append(f"\n## {loc}　{title}" + ("" if under_review else "　〔上下文：讀過，不審〕"))
        lines += [f"[{lc}] {tx}" for lc, tx in units]
    return "\n".join(lines) + "\n"


def read_report(path):
    flags, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = FLAG.match(line.strip())
        if m:
            cur = norm(m.group(2))
            flags[cur] = [m.group(1), set()]
        elif cur and line.startswith(" "):
            flags[cur][1] |= set(re.findall(r"\bR\d+\b", line))
        elif line.strip().startswith("最難讀"):
            cur = None
    return flags


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    cs = cases(sys.argv[2:])
    if cmd == "list":
        for c in cs:
            _, targets = build(c)
            print(f"{c['id']}\t{c['page']}@{c['ref']}\t{c['chapter']}\t{c.get('rules', '')}\tin_prompt={c.get('in_prompt', 'no')}")
            for loc, tx in targets:
                print(f"    [{loc}] {tx[:60]}…")
    elif cmd == "pack":
        OUT.mkdir(parents=True, exist_ok=True)
        for c in cs:
            groups, _ = build(c)
            p = OUT / f"{c['id']}-pack.md"
            p.write_text(render(c, groups), encoding="utf-8")
            n = sum(len(u) for _, _, u, r in groups if r)
            print(f"{p.relative_to(ROOT)}\t審 {n} 個單位\t報告寫到 {(OUT / (c['id'] + '-report.md')).relative_to(ROOT)}")
    elif cmd == "score":
        rows = []
        for c in cs:
            rep = OUT / f"{c['id']}-report.md"
            if not rep.exists():
                rows.append((c, None, "", ""))
                continue
            _, targets = build(c)
            flags = read_report(rep)
            hit = [(norm(loc), flags[norm(loc)]) for loc, _ in targets if norm(loc) in flags]
            blocked = [h for h in hit if h[1][0] == "BLOCK"]
            fired = set().union(*[h[1][1] for h in hit]) if hit else set()
            want = set(c.get("rules", "").split())
            rows.append((c, bool(blocked), " ".join(sorted(fired & want, key=lambda r: int(r[1:]))),
                         " ".join(sorted(want - fired, key=lambda r: int(r[1:])))))
        print("| 案例 | 寫進 prompt | 抓到 | 對上的條目 | 沒對上的條目 |\n|---|---|---|---|---|")
        for c, ok, got, miss in rows:
            mark = "（沒有報告）" if ok is None else ("是" if ok else "**否**")
            print(f"| {c['id']} | {c.get('in_prompt', 'no')} | {mark} | {got} | {miss} |")
        done = [(c, ok) for c, ok, _, _ in rows if ok is not None]
        held = [(c, ok) for c, ok in done if c.get("in_prompt", "no") != "yes"]
        for name, grp in (("全部", done), ("沒寫進 prompt 的", held)):
            if grp:
                k = sum(1 for _, ok in grp if ok)
                print(f"\n{name}：{len(grp)} 個案例，審查者抓到 {k} 個（{100 * k // len(grp)}%）"
                      + ("；漏掉：" + "、".join(c["id"] for c, ok in grp if not ok) if k < len(grp) else ""))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
