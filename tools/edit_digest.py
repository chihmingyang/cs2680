#!/usr/bin/env python3
"""James 親手改的 commit，印成讀者看得到的 before／after，給 learn-from-edit skill 用（唯讀，只有 mark 會寫檔）。

James 的改稿 = commit 訊息以「網頁編輯：」（站台編輯器自動加）或「改稿：」（他在本機或 GitHub 上改）開頭。
處理過的 commit 記在 guide/edit_log.tsv，list 不再列。

Usage:
  python3 -I tools/edit_digest.py list                 # 還沒處理的改稿 commit
  python3 -I tools/edit_digest.py show <sha>           # 一個 commit：每個改動的位置（頁、章、錨點）＋字級 diff
  python3 -I tools/edit_digest.py show <sha> --html    # 同上，但比對 HTML 原始碼（看紅字、連結、標籤的改動）
  python3 -I tools/edit_digest.py mark <sha> <類別> <一句話：學到什麼、改了哪裡>

show 的 diff 記號：[-刪掉的-]{+加上的+}；**…** 是紅字或粗體。
類別（mark 用）：typo、語句、缺context、刪支線、數字、紅字、結構、事實、品味、其他。
"""
import difflib
import html
import re
import subprocess
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "guide" / "edit_log.tsv"
PREFIXES = ("網頁編輯：", "網頁編輯:", "改稿：", "改稿:")
BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "summary", "td", "th", "dt", "dd", "pre", "blockquote"}
SKIP = {"script", "style", "svg", "nav"}


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout


def done():
    if not LOG.exists():
        return set()
    return {ln.split("\t")[0] for ln in LOG.read_text(encoding="utf-8").splitlines()[1:] if ln.strip()}


def edit_commits():
    out = git("log", "--format=%h%x09%ad%x09%s", "--date=short")
    for ln in out.splitlines():
        h, d, s = ln.split("\t", 2)
        if s.startswith(PREFIXES):
            yield h, d, s


class Blocks(HTMLParser):
    """把頁面切成讀者看得到的區塊：(位置, 文字)。位置是最近的章 id 與最近的錨點 id。"""

    def __init__(self, keep_html=False):
        super().__init__(convert_charrefs=False)
        self.keep_html = keep_html
        self.out, self.stack, self.skip = [], [], 0
        self.chapter = self.anchor = ""
        self.buf = None

    def flush(self):
        if self.buf is not None:
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if t:
                self.out.append((f"#{self.anchor or '-'}", t))
        self.buf = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP:
            self.skip += 1
            if tag == "svg" and self.buf is not None and not self.skip - 1:
                self.buf.append(f"[FIG: {a.get('aria-label', '')}]")
            return
        if self.skip:
            return
        i = a.get("id")
        if i:
            self.anchor = i
        if tag in BLOCKS:
            self.flush()
            self.buf = []
            self.stack.append(tag)
        elif self.buf is not None:
            if self.keep_html:
                self.buf.append(self.get_starttag_text() or "")
            elif tag in ("strong", "b"):
                self.buf.append("**")
            elif tag == "br":
                self.buf.append(" ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in BLOCKS:
            self.flush()
            if self.stack:
                self.stack.pop()
            if self.stack:          # 回到外層區塊（例如巢狀 li 之後）繼續收字
                self.buf = []
        elif self.buf is not None:
            if self.keep_html:
                self.buf.append(f"</{tag}>")
            elif tag in ("strong", "b"):
                self.buf.append("**")

    def handle_data(self, d):
        if not self.skip and self.buf is not None:
            self.buf.append(d)

    def handle_entityref(self, n):
        self.handle_data(f"&{n};" if self.keep_html else html.unescape(f"&{n};"))

    def handle_charref(self, n):
        self.handle_data(f"&#{n};" if self.keep_html else html.unescape(f"&#{n};"))


def blocks(src, keep_html):
    p = Blocks(keep_html)
    p.feed(src)
    p.flush()
    return p.out


def chardiff(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    r = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            r.append(a[i1:i2])
        if op in ("delete", "replace"):
            r.append(f"[-{a[i1:i2]}-]")
        if op in ("insert", "replace"):
            r.append(f"{{+{b[j1:j2]}+}}")
    return "".join(r)


def hints(a, b):
    """幾個機械訊號，幫忙猜他為什麼改。猜的，不是結論。"""
    h = []
    if a.replace("**", "") == b.replace("**", "") and a != b:
        return ["只動紅字／粗體"]
    na, nb = len(re.findall(r"\d", a)), len(re.findall(r"\d", b))
    if na - nb >= 3:
        h.append(f"數字變少（{na}→{nb} 個位數）")
    la, lb = len(a), len(b)
    if lb < la * 0.7:
        h.append(f"變短 {la}→{lb} 字")
    elif lb > la * 1.3:
        h.append(f"變長 {la}→{lb} 字")
    if re.search(r"[（(][^）)]{2,}[）)]", b) and not re.search(r"[（(][^）)]{2,}[）)]", a):
        h.append("加了括號說明（可能是補 context）")
    return h


def show(sha, keep_html):
    files = [f for f in git("diff", "--name-only", f"{sha}^", sha).split() if f.endswith(".html")]
    print(git("log", "-1", "--format=%h %ad %an%n%B", "--date=short", sha).strip())
    other = [f for f in git("diff", "--name-only", f"{sha}^", sha).split() if not f.endswith(".html")]
    if other:
        print("其他檔案：", " ".join(other))
    n = 0
    for f in files:
        old = git("show", f"{sha}^:{f}") if f in git("ls-tree", "-r", "--name-only", f"{sha}^") else ""
        new = git("show", f"{sha}:{f}") if f in git("ls-tree", "-r", "--name-only", sha) else ""
        A, B = blocks(old, keep_html), blocks(new, keep_html)
        sm = difflib.SequenceMatcher(None, [t for _, t in A], [t for _, t in B], autojunk=False)
        print(f"\n=== {f}")
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                continue
            olds, news = A[i1:i2], B[j1:j2]
            for k in range(max(len(olds), len(news))):
                n += 1
                o = olds[k] if k < len(olds) else None
                w = news[k] if k < len(news) else None
                loc = (w or o)[0]
                if o and w and difflib.SequenceMatcher(None, o[1], w[1], autojunk=False).ratio() >= 0.5:
                    print(f"\n[{n}] 改 {loc}  " + "；".join(hints(o[1], w[1])))
                    print("  " + chardiff(o[1], w[1]))
                elif o and w:
                    print(f"\n[{n}] 改寫 {loc}  " + "；".join(hints(o[1], w[1])))
                    print("  前：" + o[1])
                    print("  後：" + w[1])
                elif o:
                    print(f"\n[{n}] 刪 {loc}")
                    print("  [-" + o[1] + "-]")
                else:
                    print(f"\n[{n}] 加 {loc}")
                    print("  {+" + w[1] + "+}")
    print(f"\n共 {n} 處")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "show", "mark"):
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "list":
        seen = done()
        todo = [c for c in edit_commits() if c[0] not in seen]
        for h, d, s in todo:
            print(f"{h}\t{d}\t{s}")
        if not todo:
            print("沒有還沒處理的改稿")
    elif cmd == "show":
        show(sys.argv[2], "--html" in sys.argv)
    else:
        sha, cat, note = sys.argv[2], sys.argv[3], " ".join(sys.argv[4:])
        full = git("rev-parse", "--short", sha).strip()
        if not LOG.exists():
            LOG.write_text("commit\tdate\tcategory\tlearned\n", encoding="utf-8")
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{full}\t{date.today()}\t{cat}\t{note}\n")
        print("記下", full)


if __name__ == "__main__":
    main()
