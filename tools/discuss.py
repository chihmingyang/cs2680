#!/usr/bin/env python3
"""GitHub Issues as the discussion board: ONE issue per lecture, holding the 基礎題 only.

Usage:
  python3 -I tools/discuss.py docs/l09.html              # open the lecture's issue if missing, write links into the page
  python3 -I tools/discuss.py docs/l0[1-8].html --dry    # print what would be opened; change nothing
  python3 -I tools/discuss.py docs/l03.html --sync-body  # also rewrite the existing issue body from the page
  python3 -I tools/discuss.py --digest l03               # every answer of a lecture, grouped by question (Markdown, stdout)

Model (2026-10-21):
  - One issue per lecture (labels: L03). Title「[L3] <title> · 基礎題」.
  - The body lists the 3–5 基礎題 (Q1…Q5), each with its slide ref and a link to the page, and
    a reply template. Members post ONE comment each, with「### Q1」…「### Q5」headings.
  - 進階題 are not on GitHub. They stay on the page (section 5) for the live session.
  - The issue is found by the marker at the end of its body (<!-- cs2680:l03:lesson -->), so
    running this twice opens nothing new. Titles can be edited on GitHub freely.
  - On the page: every li.bq gets p.gh-talk linking to the lecture's issue; li.dq gets none;
    section 7 (#s-submit) is rebuilt with the issue link. Idempotent.
  - --digest splits each comment on its「### Qn」headings and prints the answers question by
    question; text without a heading goes under「其他」.

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
MARK = re.compile(r"<!-- cs2680:(l\d\d):lesson -->")
QHEAD = re.compile(r"^\s*#{1,6}\s*Q\s*(\d+)\b.*$", re.M | re.I)
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
    """lecture key (l03) -> issue (number, html_url, title, body, comments)"""
    found = {}
    for it in pages(f"{REPO}/issues?state=all"):
        if "pull_request" in it:
            continue
        m = MARK.search(it.get("body") or "")
        if m and m.group(1) not in found:
            found[m.group(1)] = it
    return found


def ensure_labels(names, dry):
    have = {l["name"] for l in pages(f"{REPO}/labels")}
    for name in names:
        if name in have:
            continue
        if dry:
            print(f"  would create label {name}")
            continue
        api(f"{REPO}/labels", "POST", {"name": name, "color": "C5DEF5", "description": f"CS2680 {name}"})
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
           "title": md(first(r"<h1>(.*?)</h1>", head)), "basic": [],
           "has_beyond": 'id="s-beyond"' in s}
    for m in re.finditer(r'<li class="bq" id="(b\d+)">', s):
        blk = li_block(s, m.start())
        tag = first(r'<p class="qtag">(.*?)</p>', blk)
        ref = re.search(r'<a class="ref" href="([^"]+)"[^>]*>(.*?)</a>', tag, re.S)
        topic = [t.strip() for t in md(re.sub(r'<a class="ref".*?</a>', "", tag, flags=re.S)).split("·")]
        lec["basic"].append({"id": m.group(1), "n": int(m.group(1)[1:]),
                             "text": md(first(r'<p class="qtext">(.*?)</p>', blk)),
                             "topic": " · ".join(t for t in topic if t),
                             "ref": (ref.group(1), md(ref.group(2))) if ref else None})
    if not lec["basic"]:
        raise SystemExit(f"{path.name}: no li.bq")
    return lec


# ---------- issue text ----------
def label_url(lec):
    return f"{ISSUES_URL}?q=" + quote(f"is:issue label:{lec['key'].upper()}")


def thread_title(lec):
    return f"[L{lec['no']}] {lec['title']} · 基礎題"


def thread_body(lec):
    page = f"{SITE_URL}{lec['key']}.html"
    n = len(lec["basic"])
    lines = [f"**CS2680 L{lec['no']} · {lec['title']}** · 基礎題 {n} 題", "",
             f"看 slides 前先看這 {n} 題，帶著問題去讀。看完後**每人在下面留一則**，用 `### Q1` … `### Q{n}` 當小標，"
             "一題一段。要補充就編輯自己那一則。建議先寫自己的，再看別人的。", "",
             f"進階題不在這裡。它們在[站台第 {5 if lec.get('has_beyond', True) else 4} 段]({page}#s-discuss)，讀書會當天一起討論。", ""]
    for q in lec["basic"]:
        lines += [f"### Q{q['n']} · {q['topic']}", "", "> " + q["text"].replace("\n", "\n> "), ""]
        bits = [f"[參考答案]({page}#{q['id']})"]
        if q["ref"]:
            bits.append(f"[Slides {q['ref'][1]}]({q['ref'][0]})")
        lines += ["　".join(bits), ""]
    lines += ["---", "", "**回覆範本**（複製到留言框再填）", "", "```markdown"]
    for q in lec["basic"]:
        lines += [f"### Q{q['n']}", "", ""]
    lines += ["```", "",
              "回應別人：按那一則右上角「⋯」裡的 Quote reply，或在留言裡寫 @對方的帳號。圖片或 PDF 直接拖進留言框。",
              "", f"<!-- cs2680:{lec['key']}:lesson -->"]
    return "\n".join(lines)


# ---------- writing the page ----------
def talk_p(url, n):
    return f'<p class="gh-talk"><a href="{url}" {EXT}>到 GitHub 回答這一題（Q{n}）↗</a></p>'


def submit_section(lec, url):
    n = len(lec["basic"])
    k = 5 if lec.get("has_beyond", True) else 4  # 2026-10-26: pages without 延伸思考 number 問題討論 as 第 4 段
    return f"""<section class="part" id="s-submit">
        <header class="part-head">
          <p class="kicker">{k + 2} · 大家的討論</p>
          <h2>這堂的討論</h2>
          <p class="lede">這堂一串，放在 GitHub Issues。看完 slides 後，把第 {k} 段的 {n} 題基礎題寫成一則留言，用 Q1 到 Q{n} 當小標。進階題不用先寫，讀書會當天一起討論。</p>
        </header>
        <div class="copyrow gh-row">
          <a class="copybtn" href="{url}" {EXT}>到這堂的討論串 ↗</a>
          <a class="ghostbtn" href="{ISSUES_URL}" {EXT}>全部講次的討論串 ↗</a>
        </div>
        <ul class="limits gh-how">
          <li>留言要先登入 GitHub。看討論不用登入。</li>
          <li>一人一則：討論串裡有回覆範本，複製後填上 Q1 到 Q{n}。要補充就編輯自己那一則。</li>
          <li>回應別人：按那一則「⋯」裡的 Quote reply，或寫 @對方的帳號。附件直接拖進留言框。</li>
          <li>討論是公開的：任何人都看得到內容和你的 GitHub 帳號。</li>
        </ul>
      </section>"""


def write_links(lec, url):
    path = lec["path"]
    s0 = path.read_text(encoding="utf-8")
    s = s0
    for cls in ("bq", "dq"):
        for m in list(re.finditer(rf'<li class="{cls}" id="([bq]\d+)">', s))[::-1]:
            blk = li_block(s, m.start())
            new = re.sub(r'\n?[ \t]*<p class="gh-talk">.*?</p>', "", blk, flags=re.S)
            if cls == "bq":
                link = talk_p(url, int(m.group(1)[1:]))
                j = new.rindex("</div>")
                indent = re.search(r"\n([ \t]*)$", new[:j])
                pad = indent.group(1) if indent else ""
                new = new[:j].rstrip() + "\n" + pad + "  " + link + "\n" + pad + new[j:]
            s = s[:m.start()] + new + s[m.start() + len(blk):]
    s, n = re.subn(r'<section class="part" id="s-submit">.*?</section>',
                   lambda _: submit_section(lec, url), s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"{path.name}: no section#s-submit")
    if s != s0:
        path.write_text(s, encoding="utf-8")
        return True
    return False


# ---------- digest ----------
def split_answer(body):
    """comment body -> {question number or 0: text}"""
    out, pos, cur = {}, 0, 0
    for m in QHEAD.finditer(body):
        chunk = body[pos:m.start()].strip()
        if chunk:
            out[cur] = (out.get(cur, "") + "\n\n" + chunk).strip()
        cur, pos = int(m.group(1)), m.end()
    chunk = body[pos:].strip()
    if chunk:
        out[cur] = (out.get(cur, "") + "\n\n" + chunk).strip()
    return out


def digest(key):
    threads = all_threads()
    if key not in threads:
        raise SystemExit(f"no issue for {key}")
    t = threads[key]
    comments = pages(f"{REPO}/issues/{t['number']}/comments") if t.get("comments") else []

    def when(iso):
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TPE).strftime("%m-%d %H:%M")

    qtitles = dict(re.findall(r"^### Q(\d+) · (.*)$", t.get("body") or "", re.M))
    byq = {}
    for c in comments:
        who = (c.get("user") or {}).get("login", "ghost")
        for qn, text in split_answer(c.get("body") or "").items():
            byq.setdefault(qn, []).append((who, when(c["created_at"]), text))
    now = datetime.now(TPE).strftime("%Y-%m-%d %H:%M")
    out = [f"# CS2680 L{int(key[1:])} 討論整理", "",
           f"{t['html_url']}", "",
           f"匯出時間：{now}（台北）。{len(comments)} 人留言。依題號排列。", ""]
    for qn in sorted(byq):
        head = f"## Q{qn} · {qtitles.get(str(qn), '')}".rstrip(" ·") if qn else "## 其他（沒有標題的段落）"
        out += [head, ""]
        for who, ts, text in byq[qn]:
            out += [f"### @{who} · {ts}", "", text, ""]
    print("\n".join(out))


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
    ensure_labels([l["key"].upper() for l in lecs], a.dry)
    created = 0
    for lec in lecs:
        k = lec["key"]
        title, body = thread_title(lec), thread_body(lec)
        if k in threads:
            t = threads[k]
            if a.sync_body and (t.get("body") or "").strip() != body.strip():
                if a.dry:
                    print(f"  would update body of #{t['number']} {k}")
                else:
                    api(f"{REPO}/issues/{t['number']}", "PATCH", {"body": body})
                    print(f"  updated body #{t['number']} {k}")
        elif a.dry:
            print(f"  would open {k}: {title}")
            continue
        else:
            t = open_issue(title, body, [k.upper()])
            threads[k] = t
            created += 1
            print(f"  opened #{t['number']} {k}")
        if not a.dry:
            changed = write_links(lec, t["html_url"])
            print(f"{lec['path'].name}: #{t['number']}; page {'updated' if changed else 'unchanged'}")
    print(f"opened {created} issues" + (" (dry run)" if a.dry else ""))


if __name__ == "__main__":
    main()
