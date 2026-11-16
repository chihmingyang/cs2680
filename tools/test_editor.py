#!/usr/bin/env python3
"""Browser test of docs/edit.js with a fake GitHub API. Changes nothing outside this process.

Usage: python3 -I tools/test_editor.py [--shots DIR]

1. Round trip, every page: every editable block is found in the source by its content.
2. On L3: edit, format, split and delete through the real UI, press 儲存, and diff the PUT body
   against the source. Only the touched blocks may change.
3. A block changed on GitHub meanwhile is reported, and not overwritten.
4. A fresh browser: only the pencil, edit.js not loaded; the pencil opens edit mode; 收起編輯工具 undoes it.
5. Comments: marks on the page, a new comment is an issue with the label comment, replies render escaped,
   replying drops answered, 解決 closes.
"""
import argparse
import base64
import difflib
import functools
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent / "docs"
problems = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        problems.append(what)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def save_with(page, message=None):
    page.locator(".ed-bar .ed-save").first.click()
    box = page.locator(".ed-commit-input")
    box.wait_for()
    default = box.input_value()
    if message:
        box.fill(message)
    box.press("Enter")
    return default


class FakeGitHub:
    """Enough of api.github.com for edit.js. `source` is what GET contents returns."""
    def __init__(self, source):
        self.source, self.puts, self.issues, self.comments, self.images = source, [], [], {}, []

    def handle(self, route):
        req = route.request
        url, method = req.url, req.method
        headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"}
        def reply(data, status=200):
            route.fulfill(status=status, headers=headers, content_type="application/json", body=json.dumps(data))
        if method == "OPTIONS":
            return route.fulfill(status=204, headers=headers)
        path = url.split("/repos/chihmingyang/cs2680", 1)[-1].split("?")[0]
        if path.startswith("/contents/"):
            if method == "GET":
                return reply({"sha": "abc", "content": base64.b64encode(self.source.encode()).decode()})
            body = json.loads(req.post_data)
            if path.startswith("/contents/docs/img/"):
                self.images.append({"path": path, "message": body["message"], "bytes": base64.b64decode(body["content"])})
                return reply({"commit": {"sha": "1mage"}}, 201)
            self.puts.append({"message": body["message"], "text": base64.b64decode(body["content"]).decode("utf-8"), "sha": body["sha"]})
            return reply({"commit": {"sha": "deadbeefcafe"}})
        if path == "/issues" and method == "POST":
            body = json.loads(req.post_data)
            issue = {"number": len(self.issues) + 1, "title": body["title"], "body": body["body"], "state": "open",
                     "labels": [{"name": l} for l in body["labels"]], "user": {"login": "chihmingyang"}}
            self.issues.append(issue)
            self.comments[issue["number"]] = []
            return reply(issue, 201)
        if path == "/issues":
            return reply(self.issues[::-1])
        parts = path.split("/")
        if path.endswith("/comments"):
            n = int(parts[2])
            if method == "POST":
                c = {"user": {"login": "chihmingyang"}, "body": json.loads(req.post_data)["body"]}
                self.comments.setdefault(n, []).append(c)
                return reply(c, 201)
            return reply(self.comments.get(n, []))
        if len(parts) == 5 and parts[3] == "labels" and method == "DELETE":
            issue = self.issues[int(parts[2]) - 1]
            issue["labels"] = [l for l in issue["labels"] if l["name"] != parts[4]]
            return reply(issue["labels"])
        if path.startswith("/issues/"):
            issue = self.issues[int(parts[2]) - 1]
            if method == "PATCH":
                issue.update(json.loads(req.post_data))
            return reply(issue)
        if path == "":
            return reply({"permissions": {"push": True}})
        reply({"message": "not found " + path}, 404)


def changed_lines(a, b):
    return [l for l in difflib.unified_diff(a.split("\n"), b.split("\n"), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]


def click_text(page, sel):
    """Put the caret in a block the way a mouse does."""
    page.locator(sel).first.scroll_into_view_if_needed()
    page.locator(sel).first.click()


ROUNDTRIP = """async (src) => {
  const ed = window.__cs2680ed; ed.indexBlocks();
  const index = ed.sourceIndex(src);
  const all = ed.main.querySelectorAll('p,li,h1,h2,h3,h4,h5,td,th,figcaption,blockquote,dt,dd,div');
  let blocks = 0, missed = [];
  for (const el of all) {
    if (!ed.isBlock(el)) continue;
    blocks++;
    const rec = ed.recs().get(el);
    const spans = index[rec.key];
    const span = spans && spans[rec.nth];
    if (!span) missed.push(el.tagName + ': ' + el.textContent.slice(0, 50));
  }
  const boxIdx = ed.boxIndex(src);
  let boxes = 0;
  for (const el of ed.main.querySelectorAll(ed.boxSel)) {
    const rec = ed.boxRecs().get(el);
    if (!rec) continue;
    boxes++;
    const span = boxIdx[rec.key] && boxIdx[rec.key][rec.nth];
    if (!span || span.tag !== el.tagName.toLowerCase()) missed.push('box ' + el.tagName + ': ' + el.textContent.slice(0, 50));
  }
  blocks += boxes;
  return { blocks, missed };
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots")
    args = ap.parse_args()
    httpd, port = serve()
    base = f"http://127.0.0.1:{port}"
    pages = sorted(p.name for p in SITE.glob("*.html") if "app.js" in p.read_text(encoding="utf-8"))
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # --- 4. members
        ctx = browser.new_context()
        page = ctx.new_page()
        loaded = []
        page.on("request", lambda r: loaded.append(r.url))
        page.goto(f"{base}/l03.html", wait_until="load")
        check(not any("edit." in u for u in loaded), "a fresh browser does not load edit.js / edit.css")
        check(page.locator(".ed-open").count() == 0 and page.locator(".ed-launch").count() == 1, "a fresh browser has only the pencil in the top bar")
        page.locator(".ed-launch").click()
        page.wait_for_selector(".ed-bar:not([hidden])")
        check(page.locator(".ed-launch").count() == 0 and page.locator(".ed-open").count() == 2, "the pencil loads the editor, opens edit mode, and gives way to the real buttons")
        page.reload(wait_until="load")
        page.wait_for_selector(".ed-open")
        check(page.locator(".ed-bar:not([hidden])").count() == 0, "after a reload the tools stay, edit mode does not")
        page.locator(".ed-open").last.click()          # 留言 button with no token: settings
        page.wait_for_selector(".ed-panel:not([hidden])")
        page.get_by_role("button", name="收起編輯工具").click()
        page.wait_for_selector(".ed-launch")
        check(page.locator(".ed-open").count() == 0, "收起編輯工具 goes back to the plain pencil")
        ctx.close()

        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        errors = []
        ctx.add_init_script("try{localStorage.setItem('cs2680.ed.token','test')}catch(e){}")
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))

        # --- 1. round trip on every page
        for name in pages:
            page.goto(f"{base}/{name}?edit", wait_until="load")
            page.wait_for_function("window.__cs2680ed")
            src = (SITE / name).read_text(encoding="utf-8")
            res = page.evaluate(ROUNDTRIP, src)
            check(not res["missed"], f"{name}: {res['blocks']} blocks all located" + ("" if not res["missed"] else f"; missed {res['missed'][:5]}"))

        # --- 2. real edits on L3
        src = (SITE / "l03.html").read_text(encoding="utf-8")
        gh = FakeGitHub(src)
        page.route("https://api.github.com/**", gh.handle)
        page.goto(f"{base}/l03.html?edit=now", wait_until="load")
        page.wait_for_selector(".ed-bar")
        check(page.locator(".ed-save").first.is_disabled(), "save starts disabled")

        # the chapter the test edits: the first one that has every kind of block the test touches
        # (pages get rewritten, so a fixed #i1 goes stale)
        CH = page.evaluate("""() => {
          const vis = e => e.getClientRects().length > 0;
          for (const c of document.querySelectorAll('main .idea[id]')) {
            const ps = [...c.querySelectorAll('.prose > p:not([class])')].filter(vis);
            if (ps.length >= 4 && c.querySelector('.prose li') && c.querySelector('.prose a') &&
                c.querySelector('figure.diagram figcaption') && c.querySelector('figure.file figcaption') &&
                c.querySelector('.table-wrap')) return '#' + c.id;
          }
          return '';
        }""")
        check(bool(CH), f"L3 has a chapter with every kind of block the test edits ({CH})")

        # plain typing: first prose paragraph of chapter 1
        # locators re-resolve and the editor adds classes, so pin the test's blocks with an attribute first
        page.evaluate("""(ch) => [...document.querySelectorAll(ch + ' .prose > p:not([class])')].filter(p => p.getClientRects().length).forEach((p, i) => p.setAttribute('data-t', i))""", CH)
        target = CH + " .prose > p[data-t]"
        para = page.locator('[data-t="0"]')
        para.scroll_into_view_if_needed()
        before = para.inner_text()
        para.click()
        page.keyboard.press("Control+End" if False else "End")
        page.keyboard.type("TYPEDTEXT")
        page.wait_for_timeout(400)
        # format a selection: red colour on the last word typed
        for _ in range(9):
            page.keyboard.press("Shift+ArrowLeft")
        page.locator('.ed-swatch[title^="文字顏色：藍"]').click()
        html_after = para.inner_html()
        check("color: var(--signal)" in html_after and "TYPEDTEXT" in html_after, "colour wraps the selection in a span with a theme token")
        # bold on the same selection
        page.locator(".ed-tool").first.click()
        check("<b>" in para.inner_html(), "bold wraps the selection")
        # undo twice goes back to the typed state
        page.keyboard.press("Control+z")
        check("<b>TYPED" not in para.inner_html(), "undo removes the bold")

        # Enter splits a paragraph into two
        para2 = page.locator('[data-t="1"]')
        para2.scroll_into_view_if_needed()
        para2.click()
        page.keyboard.press("End")
        page.keyboard.press("Enter")
        page.keyboard.type("NEWPARAGRAPH")
        page.wait_for_timeout(400)

        # a list item gets emptied: it must disappear from the source
        li = page.locator(f"{CH} .prose li").first
        li.scroll_into_view_if_needed()
        li_text = li.inner_text()
        li.click()
        page.keyboard.press("Control+a")
        page.keyboard.press("Delete")
        page.wait_for_timeout(400)

        # a link inside a block does not navigate while editing
        url_before = page.url
        link = page.locator(f"{CH} .prose a.ref, {CH} .prose a").first
        if link.count():
            link.scroll_into_view_if_needed()
            link.click()
            check(page.url.split("#")[0] == url_before.split("#")[0], "links do not navigate while editing")
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        if args.shots:
            page.screenshot(path=f"{args.shots}/editor-desktop.png")

        count = page.locator(".ed-dirty").count()
        check(count >= 3, f"dirty blocks are marked ({count})")
        default_msg = save_with(page, "L3 我自己寫的訊息")
        check(default_msg.startswith("L3 ") and "段" in default_msg, "commit box starts with a summary: " + default_msg)
        page.wait_for_function("document.querySelector('.ed-status').textContent.includes('已存')")
        check(len(gh.puts) == 1, "save sends one PUT")
        put = gh.puts[0]
        check(put["sha"] == "abc" and put["message"] == "網頁編輯：L3 我自己寫的訊息", "PUT carries the sha and my commit message: " + put["message"])
        diff = changed_lines(src, put["text"])
        print("\n".join("     " + l[:150] for l in diff))
        check(any("TYPEDTEXT" in l for l in diff), "typed text is in the file")
        check(any("NEWPARAGRAPH" in l for l in diff), "new paragraph is in the file")
        check(li_text[:12] not in put["text"].split(li_text[:12])[0][-1:] or put["text"].count(li_text[:12]) < src.count(li_text[:12]), "emptied list item left the file")
        check(not any("contenteditable" in l or "ed-active" in l or "ed-dirty" in l or "data-ed" in l or "spellcheck" in l for l in diff), "no editor residue in the file")
        check(len(diff) <= 9, f"diff stays small ({len(diff)} changed lines)")
        check("code.js" in put["text"] and put["text"].count("tk-") == src.count("tk-"), "code-block colouring from code.js did not leak into the file")
        # what was written reads back as the same structure: tags balanced in the saved block
        check(page.locator(".ed-bar .ed-save").is_disabled(), "save disabled again after saving")

        # --- 3. conflict: the block changed on GitHub meanwhile
        first = page.locator('[data-t="0"]')
        first.scroll_into_view_if_needed()
        first_html = first.inner_html()
        first.click()
        page.keyboard.press("End")
        page.keyboard.type("SECOND")
        page.keyboard.press("Escape")
        page.wait_for_timeout(350)
        gh.source = put["text"].replace("TYPEDTEXT", "SOMEONEELSE", 1) if "TYPEDTEXT" in put["text"] else put["text"]
        before_puts = len(gh.puts)
        save_with(page)
        page.wait_for_function("document.querySelector('.ed-status').textContent.includes('改過')")
        check(len(gh.puts) == before_puts, "a block changed upstream is not overwritten")
        check(page.locator(".ed-conflict").count() == 1, "the conflicting block is marked")

        # --- 6. delete boxes, add a paragraph, add an image
        gh2 = FakeGitHub(src)
        page.unroute("https://api.github.com/**")
        page.route("https://api.github.com/**", gh2.handle)
        page.on("dialog", lambda d: d.accept())
        page.goto("about:blank")
        page.goto(f"{base}/l03.html?edit=now", wait_until="load")
        page.wait_for_selector(".ed-bar")
        def handle_click(sel, label, nth=0):
            el = page.locator(sel).nth(nth)
            el.scroll_into_view_if_needed()
            el.hover()
            page.wait_for_timeout(200)
            page.locator(".ed-handle .ed-hbtn", has_text=label).first.click()
            page.wait_for_timeout(50)
        counts = lambda t: (t.count("<figure"), t.count('class="table-wrap"'), t.count("<details"))
        fig_text = page.locator(f"{CH} figure.diagram figcaption").first.inner_text()[:14]
        code_cap = page.locator(f"{CH} figure.file figcaption").first.inner_text()[:14]
        handle_click(f"{CH} figure.diagram", "刪除這張圖")
        check(page.locator(".ed-deleted").count() == 1, "figure is marked, not gone yet")
        handle_click(f"{CH} figure.diagram", "復原")
        check(page.locator(".ed-deleted").count() == 0 and page.locator(".ed-dirty").count() == 0, "undo a delete: nothing left to save")
        handle_click(f"{CH} figure.diagram", "刪除這張圖")
        handle_click(f"{CH} figure.file", "刪除這段 code")
        handle_click(f"{CH} .table-wrap", "刪除整張表")
        handle_click(f"{CH} .prose > p:not(.ed-deleted)", "＋段落", 2)
        page.keyboard.type("ADDEDPARA")
        page.keyboard.press("Escape")
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        tgt = page.locator(f"{CH} .prose > p:not(.ed-deleted)").nth(3)
        tgt.scroll_into_view_if_needed(); tgt.hover(); page.wait_for_timeout(200)
        with page.expect_file_chooser() as fc:
            page.locator(".ed-handle .ed-hbtn", has_text="＋圖").first.click()
        fc.value.set_files({"name": "x.png", "mimeType": "image/png", "buffer": png})
        page.wait_for_selector("figure.pasted img")
        page.locator("figure.pasted figcaption").click()
        page.keyboard.type("PICCAPTION")
        page.keyboard.press("Escape")
        page.wait_for_timeout(350)
        if args.shots:
            page.screenshot(path=f"{args.shots}/editor-delete.png")
        msg = save_with(page)
        check("刪 3 處" in msg and "加 1 段" in msg and "貼 1 張圖" in msg, "summary counts the changes: " + msg)
        page.wait_for_function("document.querySelector('.ed-status').textContent.includes('已存')")
        out = gh2.puts[0]["text"]
        a, b = counts(src), counts(out)
        check(b[0] == a[0] - 1 and b[1] == a[1] - 1 and b[2] == a[2], f"source lost exactly 1 net figure and 1 table (figures {a[0]}→{b[0]}, one pasted back; tables {a[1]}→{b[1]})")
        check(fig_text not in out and code_cap not in out, "deleted figure and code are gone from the file")
        check("ADDEDPARA" in out and "PICCAPTION" in out, "added paragraph and caption are in the file")
        check('<figure class="pasted"><img src="img/l03-' in out and "data:image" not in out and "data-ed" not in out, "image points at the uploaded file, no data URL")
        check(len(gh2.images) == 1 and gh2.images[0]["bytes"] == png and gh2.images[0]["path"].endswith(".png"), "image file is uploaded byte for byte")
        check(out.count("<") - src.count("<") < 30 and "tk-" not in out.replace(src[:0], "")[:0] and out.count("tk-") == src.count("tk-"), "no runtime markup leaked")
        check(page.locator(".ed-deleted").count() == 0, "deleted boxes leave the page after saving")
        page.locator(".ed-exit").first.click()

        # --- 7. floating pencil: appears on the first bit of upward scroll
        page.evaluate("window.scrollTo(0, 5000)")
        page.wait_for_timeout(80)
        check(page.locator(".ed-fab.is-shown").count() == 0, "pencil hidden while scrolling down")
        page.evaluate("window.scrollBy(0, -10)")
        page.wait_for_timeout(80)
        check(page.locator(".ed-fab.is-shown").count() == 1, "pencil appears after 10px of scrolling up")
        y = page.evaluate("window.pageYOffset")
        p_top = page.evaluate("(()=>{const e=[...document.querySelectorAll('main p')].find(p=>p.getBoundingClientRect().top>200);window.__p=e;return e.getBoundingClientRect().top})()")
        page.locator(".ed-fab").click()
        page.wait_for_selector(".ed-bar:not([hidden])")
        page.wait_for_timeout(150)
        p_after = page.evaluate("window.__p.getBoundingClientRect().top")
        check(abs(p_after - p_top) < 3, f"reading position holds when the toolbar opens ({p_top:.0f}→{p_after:.0f})")
        page.locator(".ed-exit").first.click()

        # --- 2b. 黑: only the selected part of a red <strong> loses its colour and keeps its weight
        page.goto("about:blank")
        page.goto(f"{base}/l03.html?edit=now", wait_until="load")
        page.wait_for_selector(".ed-bar")
        info = page.evaluate("""() => {
          const s = [...document.querySelectorAll('main .idea .prose > p strong')].find(s => s.childNodes.length === 1 && s.textContent.length >= 12);
          s.closest('p').setAttribute('data-ink', '1');
          s.setAttribute('data-ink-s', '1');
          s.scrollIntoView({ block: 'center' });
          return s.textContent;
        }""")
        page.locator('[data-ink="1"]').click()
        page.evaluate("""() => {
          const s = document.querySelector('[data-ink-s]'), t = s.firstChild;
          const r = document.createRange(); r.setStart(t, 3); r.setEnd(t, 8);
          getSelection().removeAllRanges(); getSelection().addRange(r);
        }""")
        page.locator('.ed-swatch[title^="文字顏色：黑"]').click()
        got = page.evaluate("""() => { const p = document.querySelector('[data-ink="1"]');
          return { b: [...p.querySelectorAll('b')].map(b => b.textContent), strong: [...p.querySelectorAll('strong')].map(s => s.textContent), text: p.textContent }; }""")
        check(info[3:8] in got["b"] and info[:3] in got["strong"] and info[8:] in got["strong"] and info in got["text"].replace("\n", ""),
              f"黑 turns only the selected part of a red <strong> into a black <b> ({got['b']} / {got['strong']})")
        page.locator('.ed-swatch[title^="文字顏色：藍"]').click()
        page.locator('.ed-swatch[title^="文字顏色：黑"]').click()
        check(page.locator('[data-ink="1"] span[style]').count() == 0, "黑 removes a colour span")

        # --- 5. comments (留言)
        # one comment Claude already answered, quoting a sentence that is on the page
        quote = page.evaluate("""() => { const p = [...document.querySelectorAll('main .idea .prose > p:not([class])')].find(p => p.textContent.trim().length > 40); return p.textContent.trim().slice(5, 30); }""")
        gh2.issues.append({"number": 1, "title": "[l03] 這是什麼？", "state": "open", "user": {"login": "chihmingyang"},
                           "labels": [{"name": "comment"}, {"name": "answered"}],
                           "body": "<!-- cs2680:comment file=docs/l03.html anchor= -->\n頁面：x\n\n> " + quote + "\n\n這是什麼？"})
        # a reply from a Claude session posts as the owner, with the marker; it has a script tag to prove replies are escaped
        gh2.comments[1] = [{"user": {"login": "chihmingyang"}, "body": "<!-- cs2680:claude -->\n**答案** `code`\n\n<script>window.__pwned=1</script>\n\n- 一\n- 二\n\n---\n_Generated by [Claude Code](https://claude.ai/code)_"}]
        page.goto("about:blank")
        page.goto(f"{base}/l03.html", wait_until="load")
        page.wait_for_selector(".ed-cmt-badge.is-answered")
        check(page.evaluate("CSS.highlights.get('ed-cmt-ans').size") == 1, "an answered comment highlights its quote on the page")
        check(page.locator("main .ed-cmt-badge").count() == 0, "comment badges live outside <main>, so a save never sees them")
        # select a few words of a later paragraph (a mouse drag does not select in headless Chromium)
        page.evaluate("""() => {
          const p = [...document.querySelectorAll('main .idea .prose > p:not([class])')].filter(p => p.textContent.trim().length > 40)[3];
          p.scrollIntoView({ block: 'center' });
          const t = document.createTreeWalker(p, NodeFilter.SHOW_TEXT).nextNode();
          const r = document.createRange(); r.setStart(t, 0); r.setEnd(t, Math.min(20, t.length));
          getSelection().removeAllRanges(); getSelection().addRange(r);
        }""")
        page.wait_for_selector(".ed-pop:not([hidden])")
        check(page.locator(".ed-pop").inner_text() == "留言", "selecting text offers 留言")
        page.click(".ed-pop")
        page.wait_for_selector(".ed-panel textarea")
        check(page.locator(".ed-quote").count() == 1, "the panel quotes the selection")
        if args.shots:
            page.screenshot(path=f"{args.shots}/comment-composer.png")
        page.fill(".ed-panel textarea", "這段是什麼意思？")
        page.locator(".ed-panel .ed-save").click()
        page.wait_for_selector(".ed-cmt-badge.is-waiting")
        issue = gh2.issues[-1]
        check([l["name"] for l in issue["labels"]] == ["comment"] and issue["title"].startswith("[l03] "), "a comment becomes an issue with the label comment")
        check("cs2680:comment file=docs/l03.html anchor=" in issue["body"] and "\n> " in issue["body"], "issue body carries the file, anchor and quote")
        check(page.evaluate("CSS.highlights.get('ed-cmt-wait').size") == 1, "the new comment highlights its quote")
        check("等下一次 session" in page.locator(".ed-panel .ed-note").first.inner_text(), "a new comment says it waits for the next session")
        page.locator(".ed-panel .ed-panel-x").last.click()   # the panel covers the right margin
        page.locator(".ed-cmt-badge.is-answered").click()
        page.wait_for_selector(".ed-msg.is-bot")
        bot = page.locator(".ed-msg.is-bot .ed-msg-body")
        check(bot.locator("b").count() == 1 and bot.locator("li").count() == 2, "Claude's reply renders Markdown")
        check(page.evaluate("window.__pwned") is None and bot.locator("script").count() == 0, "reply HTML is escaped")
        check("Generated by" not in bot.inner_text(), "the session's attribution footer is not shown")
        if args.shots:
            page.screenshot(path=f"{args.shots}/comment-thread.png")
        page.fill(".ed-panel textarea", "還是不懂第二句")
        page.locator(".ed-panel .ed-save").click()
        page.wait_for_function("document.querySelectorAll('.ed-msg').length === 3")
        check([l["name"] for l in gh2.issues[0]["labels"]] == ["comment"], "replying drops the label answered, so the next session answers again")
        page.locator(".ed-panel .ed-exit").click()
        page.wait_for_function("document.querySelectorAll('.ed-cmt-badge').length === 1")
        check(gh2.issues[0]["state"] == "closed", "解決 closes the issue and removes its mark")
        check(page.evaluate("CSS.highlights.get('ed-cmt-wait').size") == 1, "the other comment keeps its mark")

        # --- narrow screen and dark mode
        if args.shots:
            m = browser.new_context(viewport={"width": 390, "height": 800}, color_scheme="dark")
            m.add_init_script("localStorage.setItem('cs2680.ed.token','test')")
            mp = m.new_page()
            mp.goto(f"{base}/l03.html?edit=now", wait_until="load")
            mp.wait_for_selector(".ed-bar")
            check(mp.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "no sideways scroll at 390px with the toolbar")
            mp.screenshot(path=f"{args.shots}/editor-phone-dark.png")
            m.close()

        check(not errors, f"no page errors {errors[:3]}")
        browser.close()
    httpd.shutdown()
    print("\nPROBLEMS: " + str(len(problems)) if problems else "\nALL OK")
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
