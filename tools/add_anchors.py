#!/usr/bin/env python3
"""Give the ideas and terms of an article page stable anchors.

Usage: python3 -I add_anchors.py site/l01.html [site/l02.html ...]

  section#s-ideas      div.idea      -> id="i1", "i2", ...
  section#s-beyond     div.idea      -> id="x1", "x2", ...
  section#s-background dl.terms > div -> id="t1", "t2", ...

The index page links its course-map chips to these anchors.
Existing ids on those elements are replaced, so the script is idempotent.
It also prints each anchor with its heading, for picking chip targets.
"""
import re
import sys
from pathlib import Path


def section_span(text, sid):
    m = re.search(r'<section[^>]*id="%s"' % sid, text)
    if not m:
        return None
    end = text.find("</section>", m.end())
    return m.start(), end


def strip_tags(s):
    s = re.sub(r"<small>.*?</small>", "", s, flags=re.S)
    s = re.sub(r'<a class="ref".*?</a>', "", s, flags=re.S)
    return re.sub(r"<[^>]+>", "", s).strip()


def number(text, sid, open_pat, prefix, head_pat):
    span = section_span(text, sid)
    if not span:
        return text, []
    start, end = span
    body = text[start:end]
    found = []
    counter = [0]

    def repl(m):
        counter[0] += 1
        return m.group(1) + ' id="%s%d"' % (prefix, counter[0]) + m.group(2)

    body = re.sub(open_pat, repl, body)
    for m in re.finditer(r'id="(%s\d+)"' % prefix, body):
        h = re.search(head_pat, body[m.end():], re.S)
        found.append((m.group(1), strip_tags(h.group(1)) if h else ""))
    return text[:start] + body + text[end:], found


def main(paths):
    for p in paths:
        path = Path(p)
        text = path.read_text(encoding="utf-8")
        listing = []
        text, a = number(text, "s-ideas", r'(<div class="idea")(?: id="[^"]*")?(>)', "i", r"<h3>(.*?)</h3>")
        text, b = number(text, "s-beyond", r'(<div class="idea")(?: id="[^"]*")?(>)', "x", r"<h3>(.*?)</h3>")
        # terms: the <div> rows directly inside dl.terms
        span = section_span(text, "s-background")
        c = []
        if span:
            s, e = span
            body = text[s:e]
            dl = re.search(r'<dl class="terms">(.*?)</dl>', body, re.S)
            if dl:
                inner = dl.group(1)
                k = [0]

                def rep(m):
                    k[0] += 1
                    return '<div id="t%d">' % k[0]

                inner2 = re.sub(r'<div(?: id="[^"]*")?>', rep, inner)
                body = body[:dl.start(1)] + inner2 + body[dl.end(1):]
                for m in re.finditer(r'<div id="(t\d+)">\s*<dt>(.*?)</dt>', inner2, re.S):
                    c.append((m.group(1), strip_tags(m.group(2))))
            text = text[:s] + body + text[e:]
        path.write_text(text, encoding="utf-8")
        listing = a + b + c
        print("==", path.name)
        for anchor, head in listing:
            print("  #%-4s %s" % (anchor, head))


if __name__ == "__main__":
    main(sys.argv[1:])
