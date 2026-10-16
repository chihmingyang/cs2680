#!/usr/bin/env bash
# Run punctuation normalization and validation on every finished lecture page.
cd "$(dirname "$0")/.." || exit 1
declare -A PAGES=([l01]=52 [l02]=60 [l03]=83 [l04]=58 [l05]=49 [l06]=33 [l07]=38 [l08]=61)
declare -A PDF=([l01]=1_intro.pdf [l02]=2_agent_use_1.pdf [l03]=3_agent_use_2.pdf [l04]=4_agent_design_1.pdf [l05]=5_agent_design_2.pdf [l06]=6_agent_design_3.pdf [l07]=7_agent_design_4.pdf [l08]=8_agent_design_5.pdf)
for k in l01 l02 l03 l04 l05 l06 l07 l08; do
  f="site/$k.html"
  [ -f "$f" ] || { echo "$k: missing"; continue; }
  python3 -I tools/punct.py "$f" >/dev/null
  python3 -I tools/check.py "$f" --pages "${PAGES[$k]}" --pdf "${PDF[$k]}" --fix-time | sed "s/^/  /" | grep -E "slide entries|reading time|LONG|filler|PROBLEMS|  - |OK$"
done
