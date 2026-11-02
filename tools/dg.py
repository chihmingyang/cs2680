#!/usr/bin/env python3
"""Helpers for drawing the site's inline SVG diagrams in the v6/v7 style (STYLE_ARTICLE 第 6 節).

Use it from a one-off build script in notes/ (notes/ is not committed):

    import sys; sys.path.insert(0, 'tools')
    from dg import G, fig, band, reuse
    g = G(720, 216, 'l3c-sup', 'aria-label：把圖用文字講一遍')
    g.line([(140, 118), (140, 88), (580, 88), (580, 118)], end=False)   # right-angle connector, no arrow
    g.box(280, 14, 160, 42, 'focus', 'Supervisor')                    # deep red, white text
    g.box(50, 118, 180, 42, 'a', 'Researcher')                        # pale fills: a 青, b 黃, c 藍, d 粉, n 灰
    band(g, 50, 202, '事先拆好', '一個 supervisor', '星狀，全部經過中心')   # Task / Control / Comms strip
    html = fig(g, 'figcaption：先說這張圖回答什麼，再說結論。')

Draw lines before boxes so boxes cover line ends. Text classes: dg-h (heading 15px), dg-l (box label 15px),
dg-ls (small box label 13px), dg-c (note 13px), dg-cb (bold note), dg-k (deep red note), dg-mn (mono 12px).
Keep technical terms in English inside figures (heartbeat, lease, merge, read-only).
After building, run: python3 -I tools/check_diagrams.py docs/lXX.html
"""
import re

KINDS = {'focus', 'a', 'b', 'c', 'd', 'n'}


class G:
    """One svg. Marker ids get the prefix, which must be unique across the whole site (audit.py checks)."""

    def __init__(self, w, h, prefix, aria):
        self.w, self.h, self.p, self.aria, self.e = w, h, prefix, aria, []

    def panel(self, x, y, w, h):
        self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="dg-panel"/>')

    def rect(self, x, y, w, h, kind, rx=4):
        assert kind in KINDS, kind
        r = f' rx="{rx}"' if rx else ''
        self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{r} class="dg-n-{kind}"/>')

    def t(self, x, y, text, cls='dg-c', a=None):
        anchor = f' text-anchor="{a}"' if a else ''
        self.e.append(f'<text x="{x}" y="{y}"{anchor} class="{cls}">{text}</text>')

    def box(self, x, y, w, h, kind, label, sub=None, cls=None):
        """A filled box with centered text; a focus box gets white text. sub adds a second, smaller line."""
        self.rect(x, y, w, h, kind)
        lc = cls or ('dg-l-on' if kind == 'focus' else 'dg-l')
        cx = x + w / 2
        cx = int(cx) if cx == int(cx) else cx
        if sub:
            self.t(cx, y + h / 2 - 3, label, lc, 'middle')
            self.t(cx, y + h / 2 + 14, sub, 'dg-c-on' if kind == 'focus' else 'dg-c', 'middle')
        else:
            self.t(cx, y + h / 2 + 5, label, lc, 'middle')

    def line(self, pts, key=False, start=False, end=True, dash=False, cls=None):
        """A polyline through pts. key=True draws the deep red emphasis line; prefer right angles."""
        d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        c = cls or ('dg-link-key' if key else 'dg-link')
        if dash:
            c += ' dg-dash'
        m = f'{self.p}-ak' if key else f'{self.p}-ah'
        ms = f' marker-start="url(#{m})"' if start else ''
        me = f' marker-end="url(#{m})"' if end else ''
        self.e.append(f'<path d="{d}" class="{c}"{ms}{me}/>')

    def svg(self):
        defs = (
            '<defs>'
            f'<marker id="{self.p}-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="dg-fill-link"/></marker>'
            f'<marker id="{self.p}-ak" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="dg-fill-key"/></marker>'
            '</defs>'
        )
        ind = '\n                  '
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{self.aria}">{ind}{defs}{ind}'
                + ind.join(self.e) + '\n                </svg>')


def fig(g, caption):
    """Wrap an svg as figure.diagram. The caption says what question the figure answers, then the conclusion."""
    return ('<figure class="diagram">\n              <div class="scroll">\n                '
            + g.svg() + '\n              </div>\n              <figcaption>' + caption + '</figcaption>\n            </figure>')


def band(g, x, y, task, control, comms):
    """The slide-style bottom strip for an architecture figure: its answer on the three graphs."""
    g.rect(x, y - 14, 3, 19, 'focus', rx=0)
    g.t(x + 11, y, f'<tspan class="dg-cb">Task</tspan> {task} · <tspan class="dg-cb">Control</tspan> {control} · <tspan class="dg-cb">Comms</tspan> {comms}')


def figures(html):
    """All figure.diagram blocks of a page, in order, so a rewrite can reuse existing figures."""
    return re.findall(r'<figure class="diagram[^"]*".*?</figure>', html, re.S)


def reuse(figure_html, caption, old_prefix, new_prefix, strip_pages=True):
    """Reuse an existing figure under a new caption. Renames marker ids and, by default, drops slide page numbers."""
    v = re.search(r'<svg.*?</svg>', figure_html, re.S).group(0).replace(old_prefix, new_prefix)
    if strip_pages:
        v = re.sub(r'（p\.\d+(?:–\d+)?）', '', v)
        v = re.sub(r'p\.\d+(?:–\d+)? ?的例子', '例子', v)
        v = re.sub(r'p\.\d+：', '', v)
    return '<figure class="diagram">\n<div class="scroll">\n' + v + '\n</div>\n<figcaption>' + caption + '</figcaption>\n</figure>'
