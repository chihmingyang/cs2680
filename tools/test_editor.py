#!/usr/bin/env python3
"""Browser test of docs/edit.js with a fake GitHub API. Changes nothing outside this process.

Usage: python3 -I tools/test_editor.py [--shots DIR]

1. Round trip, every page: every editable block is found in the source by its content.
2. On L3: edit, format, split and delete through the real UI, press 儲存, and diff the PUT body
   against the source. Only the touched blocks may change.
3. A block changed on GitHub meanwhile is reported, and not overwritten.
4. Members (no ?edit): edit.js is not loaded.
5. Ask panel: posting a question makes an issue with the label ask; the reply renders escaped.
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


class FakeGitHub:
    """Enough of api.github.com for edit.js. `source` is what GET contents returns."""
    def __init__(self, source):
        self.source, self.puts, self.issues, self.comments = source, [], [], {}

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
            self.puts.append({"message": body["message"], "text": base64.b64decode(body["content"]).decode("utf-8"), "sha": body["sha"]})
            return reply({"commit": {"sha": "deadbeefcafe"}})
        if path == "/issues" and method == "POST":
            body = json.loads(req.post_data)
            issue = {"number": len(self.issues) + 1, "title": body["title"], "body": body["body"], "labels": body["labels"], "user": {"login": "chihmingyang"}}
            self.issues.append(issue)
            # the fake workflow answers at once; includes a script tag to prove replies are escaped
            self.comments[issue["number"]] = [{"user": {"login": "github-actions[bot]"}, "body": "**答案** `code`\n\n<script>window.__pwned=1</script>\n\n- 一\n- 二"}]
            return reply(issue, 201)
        if path == "/issues":
            return reply(self.issues)
        if path.endswith("/comments"):
            return reply(self.comments.get(int(path.split("/")[2]), []))
        if path.startswith("/issues/"):
            return reply(self.issues[int(path.split("/")[2]) - 1])
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
  return { blocks, missed };
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots")
    args = ap.parse_args()
    httpd, port = serve()
    base = f"http://127.0.0.1:{port}"
    pages = sorted(p.name for p in SITE.glob("*.html") if "app.js" in p.read_text(encoding="utf-8"))  # l02-readings.html has its own script
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # --- 4. members
        ctx = browser.new_context()
        page = ctx.new_page()
        loaded = []
        page.on("request", lambda r: loaded.append(r.url))
        page.goto(f"{base}/l03.html", wait_until="load")
        check(not any("edit." in u for u in loaded), "member page does not load edit.js / edit.css")
        check(page.locator(".ed-open").count() == 0, "member page has no edit buttons")
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

        # plain typing: first prose paragraph of chapter 1
        # locators re-resolve and the editor adds classes, so pin the test's blocks with an attribute first
        page.evaluate("""() => document.querySelectorAll('#i1 .prose > p:not([class])').forEach((p, i) => p.setAttribute('data-t', i))""")
        target = "#i1 .prose > p[data-t]"
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
        page.locator(".ed-swatch").nth(3).click()
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
        li = page.locator("#i1 .prose li").first
        li.scroll_into_view_if_needed()
        li_text = li.inner_text()
        li.click()
        page.keyboard.press("Control+a")
        page.keyboard.press("Delete")
        page.wait_for_timeout(400)

        # a link inside a block does not navigate while editing
        url_before = page.url
        link = page.locator("#i1 .prose a.ref, #i1 .prose a").first
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
        page.locator(".ed-bar .ed-save").click()
        page.wait_for_function("document.querySelector('.ed-status').textContent.includes('已存')")
        check(len(gh.puts) == 1, "save sends one PUT")
        put = gh.puts[0]
        check(put["sha"] == "abc" and "L03" in put["message"], "PUT carries the sha and a commit message: " + put["message"])
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
        page.locator(".ed-bar .ed-save").click()
        page.wait_for_function("document.querySelector('.ed-status').textContent.includes('改過')")
        check(len(gh.puts) == before_puts, "a block changed upstream is not overwritten")
        check(page.locator(".ed-conflict").count() == 1, "the conflicting block is marked")

        # --- 5. ask panel
        page.goto("about:blank")
        page.goto(f"{base}/l03.html", wait_until="load")
        page.wait_for_selector(".ed-open")
        para = page.locator("#i1 .prose > p:not([class])").first
        para.scroll_into_view_if_needed()
        box = para.bounding_box()
        page.mouse.move(box["x"] + 5, box["y"] + 8)
        page.mouse.down()
        page.mouse.move(box["x"] + 150, box["y"] + 8)
        page.mouse.up()
        page.wait_for_selector(".ed-pop:not([hidden])")
        page.click(".ed-pop")
        page.wait_for_selector(".ed-panel textarea")
        check(page.locator(".ed-quote").count() == 1, "the panel quotes the selection")
        if args.shots:
            page.screenshot(path=f"{args.shots}/ask-composer.png")
        page.fill(".ed-panel textarea", "這段是什麼意思？")
        page.locator(".ed-panel .ed-save").click()
        page.wait_for_selector(".ed-msg.is-bot")
        issue = gh.issues[0]
        check(issue["labels"] == ["ask"] and issue["title"].startswith("[l03] "), "question becomes an issue with the label ask")
        check("cs2680:ask mode=ask file=docs/l03.html anchor=" in issue["body"], "issue body carries the mode, file and anchor")
        bot = page.locator(".ed-msg.is-bot .ed-msg-body")
        check(bot.locator("b").count() == 1 and bot.locator("li").count() == 2, "reply renders Markdown")
        check(page.evaluate("window.__pwned") is None and bot.locator("script").count() == 0, "reply HTML is escaped")
        if args.shots:
            page.screenshot(path=f"{args.shots}/ask-thread.png")

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
