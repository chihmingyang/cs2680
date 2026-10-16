#!/usr/bin/env python3
"""End-to-end test of the slide + notes reader on a local HTTP server.

Usage: python3 -I test_deck.py SITE_DIR PAGE.html TEST_PDF SHOT_DIR
Checks: initial notes-only state, loading via the file input, lazy rendering of
every page, restore from IndexedDB after reload, phone layout, page errors.
"""
import subprocess
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

site, page_name, pdf, shots = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
shots.mkdir(parents=True, exist_ok=True)
port = 8765
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                       cwd=site, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
url = f"http://127.0.0.1:{port}/{page_name}"
errors = []


def scroll_all(pg):
    h = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < h:
        pg.evaluate(f"window.scrollTo(0, {y})")
        pg.wait_for_timeout(120)
        y += 700
        h = pg.evaluate("document.documentElement.scrollHeight")
    pg.wait_for_timeout(800)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme="light")
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
        pg.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" and "fonts.g" not in m.text else None)
        pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        pg.goto(url)
        pg.wait_for_timeout(400)
        visible_rows = pg.evaluate("[...document.querySelectorAll('.srow')].filter(r => r.offsetParent).length")
        print("before load: has-pdf =", pg.evaluate("document.documentElement.classList.contains('has-pdf')"),
              "| visible rows =", visible_rows)
        pg.screenshot(path=str(shots / "deck-before.png"))

        pg.set_input_files("#pdf-input", str(pdf))
        pg.wait_for_function("document.documentElement.classList.contains('has-pdf')", timeout=15000)
        pg.wait_for_selector(".frame.ready", timeout=15000)
        print("after load: loader text =", pg.inner_text(".loader-done").strip().replace("\n", " "))
        scroll_all(pg)
        print("rendered frames:", pg.evaluate("document.querySelectorAll('.frame.ready').length"),
              "/", pg.evaluate("document.querySelectorAll('.frame').length"),
              "| missing:", pg.evaluate("document.querySelectorAll('.frame.missing').length"))
        pg.evaluate("document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.getElementById('p7').getBoundingClientRect().top + scrollY - 70)")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(shots / "deck-desktop.png"))
        print("desktop scrollWidth:", pg.evaluate("document.documentElement.scrollWidth"))

        pg.reload()
        pg.wait_for_function("document.documentElement.classList.contains('has-pdf')", timeout=15000)
        pg.wait_for_selector(".frame.ready", timeout=15000)
        print("after reload: restored from IndexedDB =", pg.evaluate("document.documentElement.classList.contains('has-pdf')"))

        pg.click("#pdf-clear")
        pg.wait_for_timeout(300)
        print("after remove: has-pdf =", pg.evaluate("document.documentElement.classList.contains('has-pdf')"))
        ctx.close()

        ctx2 = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="dark", device_scale_factor=2)
        ph = ctx2.new_page()
        ph.on("pageerror", lambda e: errors.append("phone pageerror: " + str(e)))
        ph.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        ph.goto(url)
        ph.set_input_files("#pdf-input", str(pdf))
        ph.wait_for_selector(".frame.ready", timeout=15000)
        ph.evaluate("document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.getElementById('p8').getBoundingClientRect().top + scrollY - 70)")
        ph.wait_for_timeout(800)
        ph.screenshot(path=str(shots / "deck-phone.png"))
        print("phone scrollWidth:", ph.evaluate("document.documentElement.scrollWidth"))
        ctx2.close()
        b.close()
finally:
    srv.terminate()

print("errors:", errors if errors else "none")
