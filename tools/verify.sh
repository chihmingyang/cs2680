#!/usr/bin/env bash
# 一次跑完一堂的六個檢查，只印有問題的部分；全部通過只印一行 ALL OK。
#
# 用法：bash tools/verify.sh l03
#
# 為什麼：分開跑是六個 tool call，每個 call 都要重讀整個 context；合成一個，每輪檢查只花一步。
# 跑的是：check_article、check_discuss、check_diagrams、audit、add_lecture --check、punct --diff（只提示）。
# 不寫回任何檔案（check_article 不帶 --fix-time，punct 只用 --diff）。
# 不包含 discuss.py --sync-body：它要連 GitHub、改的是 issue，改了基礎題才另外跑。
# 通過但有 warn 的檢查，會印出 warn 讓你看一次。
set -u
cd "$(dirname "$0")/.."
L=${1:?用法：bash tools/verify.sh lXX}
P=docs/$L.html
[ -f "$P" ] || { echo "找不到 $P"; exit 2; }
PDF=$(grep -o 'slides/[^"#]*\.pdf' "$P" | head -1)
PAGES=$(sed -n 4p "slides/$L-notes.md" 2>/dev/null | grep -o '[0-9]\+' | head -1)
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

if [ -n "$PDF" ] && [ -n "$PAGES" ]; then
  run check_article '^OK$' python3 -I tools/check_article.py "$P" --pages "$PAGES" --pdf "$PDF"
else
  run check_article '^OK$' python3 -I tools/check_article.py "$P"
fi
run check_discuss  '^OK$'                 python3 -I tools/check_discuss.py "$P"
run check_diagrams '^OK$'                 python3 -I tools/check_diagrams.py "$P"
run audit          '^NO PROBLEMS$'        python3 -I tools/audit.py
run add_lecture    'nothing \(in sync\)'  python3 -I tools/add_lecture.py --check
# punct 只提示、不算失敗：頁面裡有故意保留的半形標點（算式、引用原文的標題）。
pd=$(python3 -I tools/punct.py "$P" --diff 2>&1)
if ! printf '%s\n' "$pd" | head -1 | grep -q ': 0 text nodes would change$'; then
  echo "note punct（只看自己這次改的；引用原文或算式的半形標點要保留）"
  printf '%s\n' "$pd" | head -20
fi

[ $fail -eq 0 ] && echo "ALL OK" || exit 1
