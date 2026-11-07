#!/usr/bin/env python3
"""Compare several readability-review reports of the SAME pack: how noisy is the reviewer?

Usage:
  python3 -I tools/review_noise.py notes/review/l06-noise-r1.md notes/review/l06-noise-r2.md notes/review/l06-noise-r3.md

Why: a regression gate built on the reviewer ("BLOCK count must not go up", WORKFLOW J layer 3)
only means something if the count does not swing on its own. This reads N reports of one
unchanged pack and prints, per run, the BLOCK/NIT counts, then how much the runs agree on
WHICH units are blockers (not just how many): units flagged by every run, by some, by one;
pairwise Jaccard overlap; and the overlap of the "最難讀的三處" lists.
Read-only; prints a Markdown summary.
"""
import itertools
import re
import sys
from pathlib import Path

LOC = re.compile(r'^(BLOCK|NIT) \[([^\]]+)\]')
TOP = re.compile(r'^\s*\d+\.\s*\[([^\]]+)\]')


def norm(loc):
    # "[#i2 表2 列2 ‹為什麼抓不到›]" and "[#i2 表2 列2]" should count as the same table row
    loc = re.sub(r'\s*‹[^›]*›', '', loc)
    return re.sub(r'\s+', ' ', loc).strip()


def parse(path):
    blocks, nits, top, in_top = set(), set(), [], False
    for line in Path(path).read_text().splitlines():
        if line.startswith('最難讀的三處'):
            in_top = True
            continue
        m = LOC.match(line)
        if m and not in_top:
            (blocks if m.group(1) == 'BLOCK' else nits).add(norm(m.group(2)))
            continue
        m = TOP.match(line)
        if in_top and m:
            top.append(norm(m.group(1)))
    return blocks, nits, top


def jac(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def main(paths):
    runs = [parse(p) for p in paths]
    print('| run | BLOCK 單位 | NIT 單位 |\n|---|---|---|')
    for p, (b, n, _) in zip(paths, runs):
        print(f'| {Path(p).stem} | {len(b)} | {len(n)} |')
    bs = [r[0] for r in runs]
    allb = set().union(*bs)
    cnt = {u: sum(u in b for b in bs) for u in allb}
    k = len(bs)
    print(f'\nBLOCK 單位聯集 {len(allb)} 個：{k} 次都標 {sum(v == k for v in cnt.values())}，'
          f'只有 1 次標 {sum(v == 1 for v in cnt.values())}，其他 {sum(1 < v < k for v in cnt.values())}')
    for (i, a), (j, b) in itertools.combinations(enumerate(bs), 2):
        print(f'- r{i+1} vs r{j+1}：BLOCK 定位 Jaccard {jac(a, b):.2f}（共同 {len(a & b)}）')
    tops = [set(r[2]) for r in runs]
    print(f'\n最難讀的三處：三次都列的 {len(set.intersection(*tops)) if tops else 0} 處；'
          f'出現過的共 {len(set().union(*tops))} 處')
    print('\n三次都標 BLOCK 的單位：')
    for u in sorted(u for u, v in cnt.items() if v == k):
        print(f'- {u}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1:])
