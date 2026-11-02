#!/usr/bin/env python3
"""Turn one「問 Claude」issue into a prompt file for .github/workflows/ask.yml.

Usage: python3 -I tools/ask_prompt.py ISSUE_NUMBER OUT_FILE   (prints mode=ask|edit for $GITHUB_OUTPUT)

The thread keeps only the repo owner's and the workflow's own messages: anyone can comment on a
public issue, and another person's comment must not reach Claude as if James had written it.
The mode comes from the marker edit.js writes on each message; a comment typed on GitHub
has no marker and counts as ask.
"""
import json
import os
import re
import subprocess
import sys

OWNER = "chihmingyang"
BOT = "github-actions[bot]"
REPO = os.environ.get("GITHUB_REPOSITORY", "chihmingyang/cs2680")


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", "--paginate", f"repos/{REPO}/{path}"], text=True))


def strip(body):
    return re.sub(r"<!--.*?-->\s*", "", body or "", flags=re.S).strip()


def mode_of(body):
    m = re.search(r"<!-- cs2680:ask mode=(\w+)", body or "")
    return "edit" if m and m.group(1) == "edit" else "ask"


COMMON = """你在回答 James 的問題。他在讀 CS2680 讀書會站台（這個 repo 的 docs/），在頁面上發問。
這一串的內容在最下面。先讀 CLAUDE.md；問題有關哪一頁，就去讀 docs/ 裡那一頁對應的段落，需要時讀 slides/lXX-notes.md。

寫法：繁體中文。句子要接得順，名詞第一次出現時補它的來歷，不為了短句切斷語氣。可以用真實的檔案內容或指令當例子。
不要寫「根據這一頁」之類的開場，直接回答。你的最後輸出會原封不動貼成 issue 留言，所以只輸出要給他看的內容。
"""

ASK = """這次只回答，不要改任何檔案，也不要 commit。"""

EDIT = """這次要直接改站台：
1. 照 .claude/skills/rewrite-with-example/SKILL.md 找出原因、改 docs/ 裡的 HTML。規則以 guide/STYLE_ARTICLE.md 為準。
2. 跑 python3 -I tools/check_article.py docs/lXX.html 和 python3 -I tools/check_discuss.py docs/lXX.html（這個環境沒有瀏覽器，不跑 audit.py、shot_article.py）。
3. git add 改過的檔案、用中文一行訊息 commit，然後 git pull --rebase origin main，git push origin main。
4. 最後的輸出只列：原文為什麼看不懂、改了什麼、哪裡要他確認。站台約 1–2 分鐘後更新。
"""


def main():
    number, out = sys.argv[1], sys.argv[2]
    issue = api(f"issues/{number}")
    comments = api(f"issues/{number}/comments?per_page=100")
    lines, mode = [], mode_of(issue["body"])
    head = re.search(r"file=(\S+) anchor=(\S*)", issue["body"] or "")
    if head:
        lines.append(f"頁面檔案：{head.group(1)}；錨點：#{head.group(2) or '（無）'}")
    lines.append(f"\n### James\n{strip(issue['body'])}")
    for c in comments:
        who = c["user"]["login"]
        if who == OWNER:
            mode = mode_of(c["body"])
            lines.append(f"\n### James\n{strip(c['body'])}")
        elif who == BOT:
            lines.append(f"\n### Claude（之前的回覆）\n{strip(c['body'])}")
    prompt = COMMON + "\n" + (EDIT if mode == "edit" else ASK) + "\n\n---\n這一串：\n" + "\n".join(lines) + "\n"
    with open(out, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"mode={mode}")


if __name__ == "__main__":
    main()
