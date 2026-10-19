#!/usr/bin/env python3
"""GitHub Issues as the discussion board: one issue per question, one 綜合 issue per lecture.

Usage:
  python3 -I tools/discuss.py docs/l09.html              # open missing issues, write links into the page
  python3 -I tools/discuss.py docs/l0[1-8].html --dry    # print what would be opened; change nothing
  python3 -I tools/discuss.py docs/l03.html --sync-body  # also rewrite existing issue bodies from the page
  python3 -I tools/discuss.py --digest l03               # every comment of a lecture as Markdown (stdout)

What it does for each page:
  1. Reads main[data-lecture], h1, data-pdf, every li.bq#bN and li.dq#qN of section 5.
  2. Finds existing issues by the marker at the end of each body (<!-- cs2680:l03:b2 -->), so
     running it twice opens nothing new. Titles can be edited on GitHub freely.
  3. Opens missing issues with labels L03 + 基礎題 / 進階題 / 綜合. The body carries the
     question (進階題 also 情境, 回答要點與提示, 作答範本) and links back to the page.
  4. Writes p.gh-talk (到 GitHub 討論這一題 ↗) into each question card and rebuilds section 7
     (#s-submit) with the 綜合 issue and the label filter. Idempotent.

Uses only the GitHub REST API through the gh CLI (Claude sessions cannot use GraphQL).
In a Claude session: add_repo with access "push"; `gh api user` must print the account.
"""
import argparse
import html as H
import json
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

OWNER, NAME = "chihmingyang", "cs2680"
REPO = f"repos/{OWNER}/{NAME}"
SITE_URL = "https://chihmingyang.github.io/cs2680/"
ISSUES_URL = f"https://github.com/{OWNER}/{NAME}/issues"
EXT = 'target="_blank" rel="noopener"'
KIND_LABEL = {"b": "基礎題", "q": "進階題", "all": "綜合"}
LABEL_STYLE = {"基礎題": ("0E8A16", "帶著問題看 slides 的題目"),
               "進階題": ("D93F0B", "讀書會討論題"),
               "綜合": ("5319E7", "跨題的想法、整體心得與附件")}
MARK = re.compile(r"<!-- cs2680:(l\d\d:(?:b\d+|q\d+|all)) -->")
TPE = timezone(timedelta(hours=8))


# ---------- GitHub REST ----------
def api(path, method="GET", data=None):
    cmd = ["gh", "api", "-X", method, path]
    if data is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(data) if data is not None else None,
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"gh api {method} {path} failed: " + (r.stderr or r.stdout)[:400])
    return json.loads(r.stdout) if r.stdout.strip() else None


def pages(path):
    """GET every page of a list endpoint."""
    out, n = [], 1
    sep = "&" if "?" in path else "?"
    while True:
        chunk = api(f"{path}{sep}per_page=100&page={n}")
        out += chunk
        if len(chunk) < 100:
            return out
        n += 1


def all_threads():
    """marker key -> issue (number, html_url, title, body)"""
    found = {}
    for it in pages(f"{REPO}/issues?state=all"):
        if "pull_request" in it:
            continue
        m = MARK.search(it.get("body") or "")
        if m:
            found[m.group(1)] = it
    return found


def ensure_labels(names, dry):
    have = {l["name"] for l in pages(f"{REPO}/labels")}
    for name in names:
        if name in have:
            continue
        color, desc = LABEL_STYLE.get(name, ("C5DEF5", f"CS2680 {name}"))
        if dry:
            print(f"  would create label {name}")
            continue
        api(f"{REPO}/labels", "POST", {"name": name, "color": color, "description": desc})
        print(f"  label {name} created")


def open_issue(title, body, labels):
    it = api(f"{REPO}/issues", "POST", {"title": title, "body": body, "labels": labels})
    time.sleep(1.5)  # stay well under GitHub's content-creation limits
    return it


# ---------- reading the page ----------
def li_block(s, start):
    """Text of the <li ...> that starts at `start`, nested <li> included."""
    depth = 0
    for m in re.finditer(r"<li\b|</li>", s[start:]):
        depth += 1 if m.group(0) == "<li" else -1
        if depth == 0:
            return s[start:start + m.end()]
    raise SystemExit("unbalanced <li>")


def md(fragment):
    """HTML fragment -> plain Markdown text (code kept, bold dropped: CJK breaks ** flanking)."""
    s = re.sub(r"<code>(.*?)</code>", lambda m: "`" + m.group(1) + "`", fragment, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s)
    return re.sub(r"[ \t]*\n[ \t]*", "\n", re.sub(r"[ \t]+", " ", s)).strip()


def first(pat, s, default=""):
    m = re.search(pat, s, re.S)
    return m.group(1) if m else default


def read_page(path):
    s = path.read_text(encoding="utf-8")
    mm = re.search(r'<main[^>]*data-lecture="(l\d\d)"[^>]*data-pdf="([^"]+)"', s)
    if not mm:
        raise SystemExit(f"{path.name}: no main[data-lecture][data-pdf]")
    key, pdf = mm.group(1), mm.group(2)
    head = s[s.index('<header class="lecture-head">'):]
    lec = {"key": key, "no": int(key[1:]), "pdf": pdf, "path": path,
           "title": md(first(r"<h1>(.*?)</h1>", head)), "questions": []}
    for kind in ("b", "q"):
        cls = "bq" if kind == "b" else "dq"
        for m in re.finditer(rf'<li class="{cls}" id="({kind}\d+)">', s):
            blk = li_block(s, m.start())
            tag = first(r'<p class="qtag">(.*?)</p>', blk)
            ref = re.search(r'<a class="ref" href="([^"]+)"[^>]*>(.*?)</a>', tag, re.S)
            topic = [t.strip() for t in md(re.sub(r'<a class="ref".*?</a>', "", tag, flags=re.S)).split("·")]
            q = {"id": m.group(1), "kind": kind, "text": md(first(r'<p class="qtext">(.*?)</p>', blk)),
                 "topic": " · ".join(t for t in topic if t),
                 "ref": (ref.group(1), md(ref.group(2))) if ref else None}
            if kind == "q":
                q["ctx"] = re.sub(r"^情境：\s*", "", md(first(r'<p class="qctx">(.*?)</p>', blk)))
                cover = first(r'<div class="qcover">(.*?)</div>', blk)
                q["cover"] = []
                for li in re.findall(r"<li>(.*?)</li>", cover, re.S):
                    hint = re.sub(r"^提示：\s*", "", md(first(r'<span class="qh">(.*?)</span>', li)))
                    q["cover"].append((md(re.sub(r'<span class="qh">.*?</span>', "", li, flags=re.S)), hint))
                q["tpl"] = [md(t) for t in re.findall(r'<p class="tpl">(.*?)</p>', blk, re.S)]
            lec["questions"].append(q)
    return lec


# ---------- issue text ----------
REPLY_HOW = "要回應某一則，按那一則右上角「⋯」裡的 Quote reply，或在留言裡寫 @對方的帳號。"


def short(text, n=60):
    t = re.sub(r"\s+", " ", text)
    return t if len(t) <= n else t[:n - 1] + "…"


def label_url(lec):
    return f"{ISSUES_URL}?q=" + quote(f"is:issue label:{lec['key'].upper()}")


def thread_title(lec, q):
    if q is None:
        return f"[L{lec['no']} 綜合] {lec['title']}：跨題想法與附件"
    kind = "基礎" if q["kind"] == "b" else "進階"
    return f"[L{lec['no']} {kind} {q['id'][1:]}] {short(q['text'])}"


def thread_body(lec, q):
    page = f"{SITE_URL}{lec['key']}.html"
    if q is None:
        return "\n".join([
            f"**CS2680 L{lec['no']} · 綜合討論** · {lec['title']}", "",
            "這串放跨題的想法、這堂整體的心得、對別人想法的回應，以及附件。圖片或 PDF 直接拖進留言框。",
            "每一題各自的討論，在站台第 5 段每一題下面的連結。", "",
            f"- 站台：[L{lec['no']} {lec['title']}]({page})",
            f"- 這堂全部的討論串：[label:{lec['key'].upper()}]({label_url(lec)})", "",
            REPLY_HOW, "",
            f"<!-- cs2680:{lec['key']}:all -->"])
    kind = "基礎題" if q["kind"] == "b" else "進階題"
    lines = [f"**CS2680 L{lec['no']} · {kind} {q['id'][1:]}** · {q['topic']}", "",
             "> " + q["text"].replace("\n", "\n> "), ""]
    if q["kind"] == "q":
        lines += [f"**情境**：{q['ctx']}", "", "#### 回答時請涵蓋"]
        for i, (point, hint) in enumerate(q["cover"], 1):
            lines.append(f"{i}. {point}")
            if hint:
                lines.append(f"   提示：{hint}")
        if q["tpl"]:
            lines += ["", "#### 作答範本（複製到留言框再填空）", "```text", *q["tpl"], "```"]
        lines.append("")
        lines.append(f"- 題目、提示與參考觀點：[站台 L{lec['no']} 第 5 段]({page}#{q['id']})"
                     "（「參考觀點與追問」建議討論後再展開）")
    else:
        lines.append(f"- 題目與參考答案：[站台 L{lec['no']} 第 5 段]({page}#{q['id']})")
    if q["ref"]:
        lines.append(f"- Slides：[{q['ref'][1]}]({q['ref'][0]})")
    lines.append("")
    if q["kind"] == "q":
        lines.append("每人在下面寫一則回答；想補充，就編輯自己那一則。建議先寫自己的，再看別人的。")
    else:
        lines.append("看完 slides 後在下面留言：卡住的地方、跟參考答案不同的點、想再問的問題。一題可以留很多則。")
    lines += [REPLY_HOW, "", f"<!-- cs2680:{lec['key']}:{q['id']} -->"]
    return "\n".join(lines)


# ---------- writing the page ----------
def talk_p(url):
    return f'<p class="gh-talk"><a href="{url}" {EXT}>到 GitHub 討論這一題 ↗</a></p>'


def submit_section(lec, all_url):
    return f"""<section class="part" id="s-submit">
        <header class="part-head">
          <p class="kicker">7 · 大家的討論</p>
          <h2>這堂的討論</h2>
          <p class="lede">討論放在 GitHub Issues，每一題一串。第 5 段每一題下面有「到 GitHub 討論這一題」的連結。跨題的想法、這堂整體的心得和附件，寫在這堂的綜合討論串。</p>
        </header>
        <div class="copyrow gh-row">
          <a class="copybtn" href="{all_url}" {EXT}>這堂的綜合討論 ↗</a>
          <a class="ghostbtn" href="{label_url(lec)}" {EXT}>這堂全部的討論串 ↗</a>
        </div>
        <ul class="limits gh-how">
          <li>留言要先登入 GitHub。看討論不用登入。</li>
          <li>回答一題：在討論串最下面留一則。回應別人：按那一則「⋯」裡的 Quote reply，或寫 @對方的帳號。</li>
          <li>附件：把圖片或 PDF 直接拖進留言框。</li>
          <li>討論是公開的：任何人都看得到內容和你的 GitHub 帳號。</li>
        </ul>
      </section>"""


def write_links(lec, urls):
    path = lec["path"]
    s0 = path.read_text(encoding="utf-8")
    s = s0
    for q in lec["questions"]:
        cls = "bq" if q["kind"] == "b" else "dq"
        m = re.search(rf'<li class="{cls}" id="{q["id"]}">', s)
        blk = li_block(s, m.start())
        new = re.sub(r'\s*<p class="gh-talk">.*?</p>', "", blk, flags=re.S)
        link = talk_p(urls[q["id"]])
        anchor = "<details><summary>參考觀點與追問</summary>"
        if q["kind"] == "q" and anchor in new:
            i = new.index(anchor)
            indent = re.search(r"([ \t]*)$", new[:i]).group(1)
            new = new[:i] + link + "\n" + indent + new[i:]
        else:
            j = new.rindex("</div>")
            indent = re.search(r"\n([ \t]*)$", new[:j])
            pad = indent.group(1) if indent else ""
            new = new[:j].rstrip() + "\n" + pad + "  " + link + "\n" + pad + new[j:]
        s = s[:m.start()] + new + s[m.start() + len(blk):]
    s, n = re.subn(r'<section class="part" id="s-submit">.*?</section>',
                   lambda _: submit_section(lec, urls["all"]), s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"{path.name}: no section#s-submit")
    if s != s0:
        path.write_text(s, encoding="utf-8")
        return True
    return False


# ---------- digest ----------
def digest(key):
    threads = all_threads()
    keys = [k for k in threads if k.startswith(key + ":")]
    if not keys:
        raise SystemExit(f"no issues for {key}")
    rank = {"b": 0, "q": 1, "a": 2}
    keys.sort(key=lambda k: (rank[k.split(":")[1][0]], int(re.sub(r"\D", "", k.split(":")[1]) or 0)))

    def when(iso):
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TPE).strftime("%m-%d %H:%M")

    body, total = [], 0
    for k in keys:
        t = threads[k]
        body += [f"## {t['title']}", "", t["html_url"], ""]
        comments = pages(f"{REPO}/issues/{t['number']}/comments") if t.get("comments") else []
        if not comments:
            body += ["（還沒有留言）", ""]
        for c in comments:
            total += 1
            who = (c.get("user") or {}).get("login", "ghost")
            body += [f"### @{who} · {when(c['created_at'])}", "", (c.get("body") or "").strip(), ""]
    now = datetime.now(TPE).strftime("%Y-%m-%d %H:%M")
    head = [f"# CS2680 L{int(key[1:])} 討論整理", "",
            f"匯出時間：{now}（台北）。共 {len(keys)} 串、{total} 則留言。依題號排列。", ""]
    print("\n".join(head + body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--sync-body", action="store_true")
    ap.add_argument("--digest")
    a = ap.parse_args()
    if a.digest:
        digest(a.digest)
        return
    if not a.pages:
        ap.error("give lecture pages, or --digest lXX")
    lecs = [read_page(Path(p)) for p in a.pages]
    threads = all_threads()
    ensure_labels(["基礎題", "進階題", "綜合"] + [l["key"].upper() for l in lecs], a.dry)
    created = 0
    for lec in lecs:
        urls = {}
        for q in lec["questions"] + [None]:
            qid = q["id"] if q else "all"
            k = f"{lec['key']}:{qid}"
            title, body = thread_title(lec, q), thread_body(lec, q)
            if k in threads:
                t = threads[k]
                if a.sync_body and (t.get("body") or "").strip() != body.strip():
                    if a.dry:
                        print(f"  would update body of #{t['number']} {k}")
                    else:
                        api(f"{REPO}/issues/{t['number']}", "PATCH", {"body": body})
                        print(f"  updated body #{t['number']} {k}")
                urls[qid] = t["html_url"]
                continue
            if a.dry:
                print(f"  would open {k}: {title}")
                continue
            t = open_issue(title, body, [lec["key"].upper(), KIND_LABEL[q["kind"] if q else "all"]])
            threads[k] = t
            urls[qid] = t["html_url"]
            created += 1
            print(f"  opened #{t['number']} {k}")
        if not a.dry:
            changed = write_links(lec, urls)
            print(f"{lec['path'].name}: {len(urls)} issues; page {'updated' if changed else 'unchanged'}")
    print(f"opened {created} issues" + (" (dry run)" if a.dry else ""))


if __name__ == "__main__":
    main()
