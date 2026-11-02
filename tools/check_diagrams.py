#!/usr/bin/env python3
"""Geometry check for the inline SVG diagrams of a lecture page.

Usage: python3 -I tools/check_diagrams.py docs/lXX.html
Opens every details block and reports: text outside the viewBox, text that leaves its box (2 units of
margin), text overlapping text, and straight connectors running through text. Prints OK when clean.
Only looks at direct children of the svg. It does not judge how a figure looks: still read the screenshots.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

JS = r"""
// Run in the page: reports text that leaves its box or panel, text overlapping text, and connectors through text.
(() => {
  const out = [];
  document.querySelectorAll('figure.diagram svg').forEach((svg, n) => {
    const vb = svg.viewBox.baseVal;
    const texts = [...svg.querySelectorAll(':scope > text')];
    const rects = [...svg.querySelectorAll(':scope > rect')].map(r => ({x:+r.getAttribute('x'),y:+r.getAttribute('y'),w:+r.getAttribute('width'),h:+r.getAttribute('height'),c:r.getAttribute('class')}));
    const boxes = texts.map(t => { const b = t.getBBox(); return {s:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height,cx:b.x+b.width/2,cy:b.y+b.height/2}; });
    boxes.forEach(b => {
      if (b.x < 0 || b.y < 0 || b.x + b.w > vb.width || b.y + b.h > vb.height) out.push(`fig${n} outside viewBox: ${b.s}`);
      const hit = rects.filter(r => b.cx>r.x&&b.cx<r.x+r.w&&b.cy>r.y&&b.cy<r.y+r.h).sort((p,q)=>p.w*p.h-q.w*q.h)[0];
      rects.filter(r => r !== hit && r.c !== 'dg-panel' && !/dg-link|dg-frame/.test(r.c || '') && !(b.cx>r.x&&b.cx<r.x+r.w&&b.cy>r.y&&b.cy<r.y+r.h)).forEach(r => { const ox=Math.min(b.x+b.w,r.x+r.w)-Math.max(b.x,r.x), oy=Math.min(b.y+b.h,r.y+r.h)-Math.max(b.y,r.y); if (ox>1&&oy>3) out.push(`fig${n} text runs into a box: ${b.s}`); });
      if (hit) { const m = 2; if (b.x<hit.x+m||b.x+b.w>hit.x+hit.w-m) out.push(`fig${n} tight/overflow in rect w=${hit.w}: ${b.s} (text w=${b.w.toFixed(0)})`); }
    });
    for (let i=0;i<boxes.length;i++) for (let j=i+1;j<boxes.length;j++) { const a=boxes[i],c=boxes[j]; const ox=Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x), oy=Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y); if (ox>1&&oy>3) out.push(`fig${n} text overlap: ${a.s} / ${c.s}`); }
    svg.querySelectorAll(':scope > path').forEach(p => {
      const pts=[...p.getAttribute('d').matchAll(/([\d.]+),([\d.]+)/g)].map(m=>[+m[1],+m[2]]);
      for (let k=0;k<pts.length-1;k++){ const [x1,y1]=pts[k],[x2,y2]=pts[k+1]; const lx=Math.min(x1,x2),hx=Math.max(x1,x2),ly=Math.min(y1,y2),hy=Math.max(y1,y2);
        boxes.forEach(b=>{ const inRect=rects.some(r=>r.c!=='dg-panel'&&b.cx>r.x&&b.cx<r.x+r.w&&b.cy>r.y&&b.cy<r.y+r.h);
          if (x1!==x2&&y1!==y2) return; if (hx>=b.x+1&&lx<=b.x+b.w-1&&hy>=b.y+3&&ly<=b.y+b.h-3&&!inRect) out.push(`fig${n} line through text: ${b.s}`); }); }
    });
  });
  return out;
})()
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    pg.goto(Path(sys.argv[1]).resolve().as_uri()); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
    found = pg.evaluate(JS)
    b.close()
print("\n".join(found) if found else "OK")
sys.exit(1 if found else 0)
