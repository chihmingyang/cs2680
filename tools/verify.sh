#!/usr/bin/env bash
# 一次跑完一堂的六個檢查，只印有問題的部分；全部通過只印一行 ALL OK。
#
# 用法：bash tools/verify.sh l03
#       bash tools/verify.sh all    # 每一堂的頁面檢查＋全站檢查各一次（CI 用，.github/workflows/verify.yml）
#
# 為什麼：分開跑是六個 tool call，每個 call 都要重讀整個 context；合成一個，每輪檢查只花一步。
# 跑的是：check_article、check_discuss、check_diagrams、audit、add_lecture --check、dag --check、punct --diff（只提示）、
# find_figure_spots（只提示：可能該畫成圖、或表和圖重複的地方）。
# 不寫回任何檔案（check_article 不帶 --fix-time，punct 只用 --diff）。
# 不包含 discuss.py --sync-body：它要連 GitHub、改的是 issue，改了基礎題才另外跑。
# 通過但有 warn 的檢查，會印出 warn 讓你看一次。
set -u
cd "$(dirname "$0")/.."
L=${1:?用法：bash tools/verify.sh lXX（或 all）}
fail=0

run() {   # run 名稱 乾淨時最後一行要符合的-regex 指令...
  local name=$1 ok=$2; shift 2
  local out rc last w
  out=$("$@" 2>&1); rc=$?
  last=$(printf '%s\n' "$out" | tail -1)
  if [ $rc -eq 0 ] && printf '%s' "$last" | grep -Eq "$ok"; then
    w=$(printf '%s\n' "$out" | grep -c 'warn')
    if [ "$w" -gt 0 ]; then
      echo "ok   $name（$w 個 warn，看一次）"
      printf '%s\n' "$out" | grep 'warn'
    fi
  else
    fail=1
    echo "FAIL $name"
    printf '%s\n' "$out" | tail -40
  fi
}

page() {   # 一堂的頁面檢查：check_article、check_discuss、check_diagrams、punct（只提示）
  local L=$1 P=docs/$1.html PDF PAGES pd fs
  [ -f "$P" ] || { echo "找不到 $P"; fail=1; return; }
  # 頁數用頁面的 data-pages-total（兩份 deck 的 L10 是總和），沒有才讀 slides 筆記第 4 行。
  # PDF 取頁面裡所有 slides/*.pdf 的共同前綴：一份 deck 就是檔名，L10 的 2a、2b 是 10_llm_serving_basics_2。
  PDF=$(grep -o 'slides/[^"#]*\.pdf' "$P" | sort -u | python3 -I -c 'import os,sys; print(os.path.commonprefix(sys.stdin.read().split()))')
  PAGES=$(grep -o 'data-pages-total="[0-9]*"' "$P" | head -1 | grep -o '[0-9]\+')
  [ -n "$PAGES" ] || PAGES=$(sed -n 4p "slides/$L-notes.md" 2>/dev/null | grep -o '[0-9]\+' | head -1)
  if [ -n "$PDF" ] && [ -n "$PAGES" ]; then
    run check_article '^OK$' python3 -I tools/check_article.py "$P" --pages "$PAGES" --pdf "$PDF"
  else
    run check_article '^OK$' python3 -I tools/check_article.py "$P"
  fi
  run check_discuss  '^OK$'                 python3 -I tools/check_discuss.py "$P"
  run check_diagrams '^OK$'                 python3 -I tools/check_diagrams.py "$P"
  # 有題庫（<script id="quiz">）的頁面：題庫的節和頁面的小節對得上（guide/QUIZ.md）
  if grep -q 'id="quiz"' "$P"; then run quiz '^ok ' python3 -I tools/quiz.py check "$P"; fi
  # punct 只提示、不算失敗：頁面裡有故意保留的半形標點（算式、引用原文的標題）。
  pd=$(python3 -I tools/punct.py "$P" --diff 2>&1)
  if ! printf '%s\n' "$pd" | head -1 | grep -q ': 0 text nodes would change$'; then
    echo "note punct（只看自己這次改的；引用原文或算式的半形標點要保留）"
    printf '%s\n' "$pd" | head -20
  fi
  # find_figure_spots 只提示：結論是形狀才改成圖，圖要取代表或段落；判斷要留的，在那個元素加 data-no-figure。
  fs=$(python3 -I tools/find_figure_spots.py "$P" 2>&1)
  if [ "$fs" != "no candidates" ]; then
    echo "note figure-spots（看一次：結論是趨勢、轉折或最佳點才改成圖，圖要取代表或段落；決定留著的加 data-no-figure）"
    printf '%s\n' "$fs" | tail -n +2 | head -20
  fi
}

if [ "$L" = all ]; then
  for f in docs/l[0-9][0-9].html; do
    l=$(basename "$f" .html)
    out=$(page "$l"; echo "rc=$fail")
    case "$out" in *rc=1) fail=1;; esac
    out=${out%rc=*}
    [ -n "${out//[[:space:]]/}" ] && { echo "== $l"; printf '%s\n' "$out"; }
  done
else
  page "$L"
fi
run audit          '^NO PROBLEMS$'        python3 -I tools/audit.py
run add_lecture    'nothing \(in sync\)'  python3 -I tools/add_lecture.py --check
run dag            '^OK'                  python3 -I tools/dag.py --check

[ $fail -eq 0 ] && echo "ALL OK" || exit 1
