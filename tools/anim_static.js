#!/usr/bin/env node
/* 動畫圖的靜態 SVG 由 calc.js 的同一段程式產生（STYLE_ARTICLE 6〈動畫圖〉）。
 *
 * 用法：node tools/anim_static.js docs/l08.html            # 檢查：頁面裡的靜態 SVG 和 calc.js 畫的最後一格一樣，印 OK
 *       node tools/anim_static.js docs/l08.html --write    # 把靜態 SVG 換成 calc.js 畫的
 *
 * 為什麼：動畫播完要回到 HTML 裡的靜態圖，兩邊不是同一張就會跳一下；改了 calc.js 的畫法卻忘了更新 HTML，
 * 讀者沒有 JS 時、可讀性審查、check_diagrams 看到的就是舊圖。verify.sh 會跑檢查模式。
 * 每張動畫圖的預設值寫在下面的 DEFAULTS：FRAMES 的名字 → 最後一格的參數。
 */
const fs = require('fs');
const path = require('path');
const DEFAULTS = { ttl: [40, 26], resend: [5], prefix: [1, 1], decode: [52], cpath: [60, 0] };

global.window = {};
global.document = { querySelectorAll: () => [] };
require(path.join(__dirname, '..', 'docs', 'calc.js'));
const frames = global.window.cs2680Calc.frames;

const file = process.argv[2];
const write = process.argv.includes('--write');
if (!file) { console.error('用法：node tools/anim_static.js docs/lXX.html [--write]'); process.exit(2); }
let html = fs.readFileSync(file, 'utf8');
const norm = (s) => s.replace(/>\s+</g, '><').trim();
let bad = 0, n = 0;
html = html.replace(/(<figure class="diagram" data-calc="([\w-]+)">[\s\S]*?<svg\b[^>]*>)([\s\S]*?)(<\/svg>)/g, (all, head, name, body, tail) => {
  if (!frames[name]) return all;            // 滑桿圖（沒有時間軸）不歸這支管
  n++;
  const want = frames[name].apply(null, DEFAULTS[name]);
  if (norm(body) === want) return all;
  if (!write) { bad++; console.log('FAIL ' + file + ' ' + name + '：靜態 SVG 和 calc.js 的最後一格不同，跑 --write'); return all; }
  const indent = (body.match(/\n([ \t]*)</) || [0, '                  '])[1];
  const lines = want.replace(/></g, '>\n<').split('\n').map((l) => indent + l).join('\n');
  const close = (body.match(/\n([ \t]*)$/) || [0, indent.slice(2)])[1];
  return head + '\n' + lines + '\n' + close + tail;
});
if (write) fs.writeFileSync(file, html);
if (bad) process.exit(1);
console.log('OK' + (n ? '' : '（這一頁沒有動畫圖）'));
