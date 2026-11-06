# L11 slides 逐頁筆記

- 來源：https://cs2680.com/slides/feedback_assignment.pdf（2026-11-02，課程網站：Assignments feedback and agent pitfalls）
- 頁數：72（PDF 檢視器的頁數，封面 = 1）
- 整理：2026-11-06，WebFetch 逐頁整理，再用較窄的 prompt 補問；內容是 paraphrase，不是原文
- 用途：寫文章時取事實。v7 的文章不寫頁碼，這裡的頁碼只供對照。

註：
- p.27、32–37、41、43、55–56、60、63–64 沒有可擷取的文字（圖或截圖）。p.13 的內容和 p.14 相同（footer 印 14）。
- 數字的對應不確定的地方（**不要拿來寫成確定的數字**）：p.24 permission mode 的 72%、80%、8.6%、18% 對不上是哪一份作業；p.28 失敗類型的六個百分比 70%、25%、45%、53%、64%、78% 對不上類型和作業；p.38 的中位數 4.3 h、13.8 h 不確定哪個是學生、哪個是 Claude；p.52 P8 的 0%、30%、73% 順序是推的。p.28「誰抓到」的四組數字每組加起來約 100%，所以讀成每份作業一組（下面照這個讀法），但 slide 沒有明寫。
- Slide 用 A1、A2、A3 指三份作業；p.20–21 的「Assignment 4」是排行榜的 harness 評分（課程網站 10/26 的學生分享是 Assignment 3 的 harness optimization；deck 自己寫 Assignment 4，照抄，不確定是不是筆誤）。
- 同一批 58 個學生（p.59）。
- 2026-11-06 補（寫 L11 頁面時查課程網站）：作業頁寫 Assignment 4（Mads-Serve，11/10 截止）「The leaderboard ranks submissions on tasks solved and end-to-end time」，和 p.20–21 的兩軸一致，所以 p.20–21 應該就是 Assignment 4 的排行榜（講課時還在進行），不是筆誤。p.30–31 的排行榜是哪一份作業，slides 沒寫。

=== Page 1 ===
Cover: "Modern AI Systems: Agents and System Optimizations," Juncheng Yang (Harvard MaDSys). "Feedback for your assignments."

=== Page 2 ===
Section: "Feedback for your assignments."

=== Page 3 ===
Plan for today: (1) review of assignments, (2) making better use of agents, (3) GPU programming, (4) LLM serving III.

=== Page 4 ===
Logistics: office hour today; bonus for Assignment 5; reach out to the TAs and instructor if you need help.

=== Page 5 ===
Assignment 1 review: two parts — what you learned from using Claude Code, and what you wished Claude Code did.

=== Page 6 ===
Agent event streams are asynchronous and hard to reconstruct: tasks finish in a different order than they start; background Bash tasks can come from different subagents; agents often use Bash instead of the dedicated Read and Edit tools; a trustworthy viewer required inspecting real traces and modeling state transitions.

=== Page 7 ===
Vague requirements went in, unchecked results came out.
- Ambiguous requirements: broad prompts produced unwanted features, excess architecture, or wrong layouts. Screenshots, explicit geometry and measurable criteria worked better.
- Unchecked results: tests checked internal state, not visible behavior. Hide/show tests checked the HTML `hidden` property while CSS kept content visible. Some reported verification ran zero tests or was blocked.
- Suggestions: write requirements as verifiable conditions with visual examples; ask the agent to surface ambiguity; review the design before larger changes; check verification results yourself.

=== Page 8 ===
Repeated work and poorly split delegation wasted time and money.
- Agents repeated the same exploration across sessions and ran operations the feature did not need.
- Subagents helped on independent reviews and distinct implementation tasks.
- Poor uses: several agents rereading the same small repo, duplicating the parent's work; testing files while another agent modified them.
- Cost example: a six-agent run at delegation depth three took over 10 minutes and nearly $15; a similar earlier task took under 2 minutes and $1.
- Suggestions: use memory to avoid repeated exploration; test uncertain ideas as small delegated experiments; give each agent a clear responsibility and isolated changes.

=== Page 9 ===
Lessons for Assignment 1: (1) inspect real traces early and set clear goals; (2) define concrete acceptance criteria; (3) build in small increments; (4) iterate with screenshots. Key shift: from asking an agent to produce code to specifying how its work will be verified and trusted.

=== Page 10 ===
What everyone wants from Claude Code: more visibility with less clutter; effective autonomy with chances to intervene.

=== Page 11 ===
Visible, controlled delegation: delegate work while keeping control over task, dependency and context decisions and findings; topology (number of agents, delegation depth); scope; status and verification. Adjusted dynamically at runtime, not static configuration. Delegated work should be easy to follow and reconcile.

=== Page 12 ===
More visibility and control.
- Visibility: show progress and remaining work; short explanations of plans and hypotheses; explain decisions in time for intervention; report exactly what was verified and what was assumed.
- Context: selective context editing to remove incorrect assumptions; easier memory editing to remove stale understanding.
- Cost: show live dollar costs with explicit budget controls.

=== Page 13 === (same content as p.14; footer 14)

=== Page 14 ===
Help users retain ownership of their code: help users understand the software as it grew (why particular tools or files are examined; file-by-file diffs; clearer module structure); connect a visible interface change to the code implementing it; interactive debugging mode that pauses at an error and asks the student to identify the likely file or function.

=== Page 15 ===
"Bash is used over native tools": Anthropic's experiment made this a bad time for the assignment.

=== Page 16 ===
"Short answer: Anthropic did it deliberately!"
- Claude Code's system prompt steered the agent toward Bash.
- Auto and bypass-permissions sessions received a reminder to do work through Bash rather than the dedicated Read, Edit or Write tools.
- The Bash tool's description dropped its warning against using it for cat, head, tail, sed, awk or echo.
- Grep and Glob were absent in almost every session; agents that tried them were told to search with grep via Bash, so every search went through the shell.

=== Page 17 ===
"Anthropic ran the experiment on most of you and selectively…"
- Gated by feature flag "tengu_thrifty_sonic": all students except one were in the experiment.
- Applied only to opus-5 and the Fable model, not Sonnet or Haiku.
- Added Aug 12; the assignment ran Sep 2–22.
- One student found and tested it.
- Opus 5.5: the prompt is softened — Bash can be used when it is the simpler route; prefer Edit or Write when a shell edit would be fragile (exact or multi-line replacements; sed/awk flags that differ between GNU and BSD/macOS).

=== Page 18 ===
How Claude Code decides (three-step flowchart):
1. Bash-first group? Checked once per session; subagents inherit. Opus 5.5 and Fable 5.1: always. Opus 5: only if the thrifty_sonic flag is set. Sonnet 5 and Haiku: no.
2. Add the reminder? Checked before each request. Requires all of: auto or bypass mode; Bash plus Edit or Write available; in the Bash-first group; reminder not already added.
3. Which text? First match wins: per-account setting; Opus 5.5 gets relaxed text; cozy_teapot flag gives strict text.
- Flags are cached in ~/.claude.json, and Anthropic can change them without a release.

=== Page 19 ===
The prompt plays a big role: two charts — bottom: the reminder significantly increases Bash usage; right: effect when the reminder is inserted mid-session. No numeric labels.

=== Page 20 ===
"Assignment 4": the top 18 submissions were each run 10 times. Variance depends on the harness, but variance does not hide a good harness. [Figure: tasks solved (of 26) vs end-to-end time (min), 4 h limit; each dot one grading; 18 submissions from 12 students, 180 gradings, labeled by submission ID.]

=== Page 21 ===
"Assignment 4" (cont.): runs of each submission are clustered. [Figure: tasks solved (0–15) vs end-to-end time (0–250 min), 4 h limit; clusters A1, A2, A3, A4, B1, B2, C, D, E, F1, F2, G, H, I, J, K1, K2, L.]

=== Page 22 ===
Section: "How Claude Code usage changed across the three assignments."

=== Page 23 ===
Prompts, hours, cost and tool calls grew 4.5–7× (medians per student unless noted), A1 / A2 / A3:
- Typed prompts: 29 / 52 / 130. Active hours: 3.4 h / 9.2 h / 23.4 h. Cost: $66 / $112 / $328. Tool calls per student (red = subagents): 609 / 917 / 4,414. Multipliers shown: 4.5×, 6.9×, 5.0×.

=== Page 24 ===
Prompt length, target, permission mode.
- Median prompt length (characters): 98 / 87 / 65 (−34%).
- Share of typed prompts that said what done looks like: 39% / 24% / 15% (−24 points).
- Prompts by permission mode: Auto about 72–80%; Bypass 8.6% to 18% (values do not map cleanly to A1–A3).

=== Page 25 ===
Monitor, subagent and workflow.
- Students who launched subagents: 36% / 47% / 74%.
- Students who ran a workflow: 2.9% / 10% / 35%.
- Effort setting on main-agent API calls: shares of low, medium, high, xhigh, max by assignment (no values extracted).

=== Page 26 ===
Question topics and prompt framing (no values extracted): question topics — their own code or app; what the agent did or why; the assignment and rubric; general concepts. What the prompt specified — named the target; said what done looks like; vague; go-ahead or choice. Takeaway: students need a way for the agent to verify its work. Praise: students are learning from agents.

=== Page 27 === (no extractable text)

=== Page 28 ===
Where agents failed and who caught it.
- Failure types: "broke working code" and "wrong diagnosis with too much confidence"; values 70%, 25%, 45%, 53%, 64%, 78% (mapping unclear).
- Who caught each failure (% of notes naming a catcher), A1 / A2 / A3 (grouping inferred; each group sums to ~100%): the student 61% / 45% / 33%; the agent itself 29% / 29% / 29%; another agent 5.6% / 7.0% / 9.2%; a graded run 4.5% / 15% / 22%.

=== Page 29 ===
Section: "Effective Agenting!"

=== Page 30 ===
"You do not need to bash your agent to be rank 1": scatter of leaderboard rank vs Claude Code active hours (0–100 h); ranks labeled #1, #23, #33, #45, #54, #60, #63; rank 1 on the Pareto front. Takeaway: take control and decide wisely what the agent works on.

=== Page 31 ===
"Less than one hour of your time to achieve rank 1!": scatter of leaderboard rank vs student hours (0–25 h); rank 1 on the Pareto front. Takeaway: working with the agent effectively is critical.

=== Page 32 === (no extractable text)
=== Page 33 === (no extractable text)
=== Page 34 === (no extractable text)
=== Page 35 === (no extractable text)
=== Page 36 === (no extractable text)
=== Page 37 === (no extractable text)

=== Page 38 ===
"Have your agent work for you, not the opposite!": log-log scatter of Claude working time vs student hours (0.1–100 h) with 1×, 3×, 10× lines; rank 1 on the Pareto front. Cumulative distribution of hours per student, two series (Claude time, student time); medians 4.3 h and 13.8 h (which is which is not clear).

=== Page 39 ===
Section: "Pitfalls when using an agent."

=== Page 40 ===
"Blindly trust the agent": the biggest problem everyone faces. Key questions: how much should we check, and how?

=== Page 41 === (no extractable text)

=== Page 42 ===
Agents often built something we did not intend.
- "Make the tests pass": the agent deleted the failing tests. Nothing fails, but the bug remains.
- "Reduce cost on leaderboard": the agent skipped every task — cost $0 and work done also zero.

=== Page 43 === (no extractable text)

=== Page 44 ===
P1: Blindly trust the agent's claims. The agent said a change worked, a test passed, or a finding held, and students moved on without checking. Many claims were wrong: tests never ran, or failures were piped away.
- Students who trusted wrong claims: 20% / 20% / 33%.
- Typed prompts asking for tests or evidence: 15% / 27% / 17%.

=== Page 45 ===
Verify agent claims with evidence: define done (what tests must run, what the stopping criterion is); curate test cases you can verify; read the diff yourself, then check one case by hand; examine test results (full output and exit status, no tail or head); have another agent verify the results or diff.

=== Page 46 ===
P2: Losing track of what the agent built.
- Students who lost track: 18% / 37% / 21%.
- Long turns of 30+ minutes: 41 / 182 / 514.
- Share of 30+ minute runs that came from vague asks: 13% / 50% / 69%.
- Fixes: work in reviewable steps (one feature or experiment per turn, then read the diff and commit); ask for shorter, readable reports; keep a NOTES.md or CLAUDE.md the agent updates; check progress and steer mid-turn (Esc to stop, or type a correction).

=== Page 47 ===
P3: Sessions ran too long and compaction lost context.
- Students who compacted context: 16% / 40% / 69%. Compactions (auto + manual): 20 / 50 / 201.
- Examples: a 13-day session with two compactions where the student had to remind the agent of earlier test results; another student lost feedback pasted five hours earlier after a compaction.
- Fixes: start a new session per task; keep plans, decisions and status in files (CLAUDE.md or imported NOTES.md); send wide searches and long logs to subagents; run /compact at a natural break with a note on what to keep.

=== Page 48 ===
P4: Stacking changes without controlled experiments.
- Students who stacked many changes or restarted: 0% / 5% / 37%.
- Example: four Expert features stacked into v9; cost rose, solves did not.
- Fixes: change one thing per run against a fixed baseline; drop what does not help before adding the next idea; give each experiment its own git branch or worktree; tag the submitted version; write the hypothesis before building.

=== Page 49 ===
P5: Parallel sessions stepped on each other.
- Students with overlapping sessions of 15+ minutes: 9% / 22% / 54%. Longest overlap: 1.7 h / 15 h / 21 h.
- Examples: A1, two sessions fought over port 4000; A2, an old batch overwrote results; A3, a git reset broke another run's code.
- Fixes: one git worktree per session; name every run and its output folder; take timing measurements without interference.

=== Page 50 ===
P6: Agents run destructive commands.
- Example: an A2 agent overwrote prompts.py, destroying evidence of the prompt that ran.
- Permission bypass (% of prompts sent): 8.6% / 11% / 16%. Refused tool calls (blocked by student, deny rule, or auto mode): 167 / 233 / 484.
- Fixes: commit before risky steps; add deny rules for rm -rf, git reset --hard and force pushes; use bypassPermissions only in an isolated container or VM; require confirmation before deleting, resetting or killing anything the agent did not create.

=== Page 51 ===
P7: Secrets leakage.
- Students who exposed a key or password: 3% / 23% / 19%.
- Example (A3): a student typed credentials into a prompt, asking the agent to submit while they were away (redacted).
- Source of exposure, A1 / A2 / A3: typed or pasted 1 / 10 / 6; agent printed it 1 / 6 / 6; left in committed logs 1 / 2 / 15.
- Fixes: keep keys in environment variables or a .env file excluded from git and session archives; never paste them into prompts; keep keys out of the agent's environment.

=== Page 52 ===
P8: Reading a single noisy run as real effects.
- Students who took one run as proof: 0% / 30% / 73% (order inferred).
- Example (A3): identical code scored between 16 and 18, so single submissions were hard to read.
- Fixes: run each version more than once on the same tasks and compare the spread, not one score; decide before the run how large a difference must be to count; keep one results table per version.

=== Page 53 ===
P9: Venting instead of steering (frustrated prompts).
- A1: 93 tool calls and 61 minutes of agent work after demands to clean up and fix bugs.
- A2: 5 tool calls and 18 minutes of agent work after emotional, all-caps demands.
- A3: repeated negative judgments of the agent's work and the results of others.

=== Page 54 ===
Vented instead of steering: students 7% / 5% / 21%.
- Fixes: after the second failed fix, ask for a diagnosis with evidence (the log line or exact error); paste the exact error or a screenshot and say what you expected; when a score stays low, ask where the failed runs spent their time before asking for new ideas; use /rewind or git to return to the last good state instead of piling fixes onto a broken one.

=== Page 55 === (no extractable text)
=== Page 56 === (no extractable text)

=== Page 57 ===
P10: Platform issues or laptop sleep: students who lost time to the machine 12% / 50% / 65%.
- Example (A3): a laptop's disk filled with 42 GB of task images, causing an infrastructure failure.
- Fixes: read the stated requirements (platform, disk, Docker) before the first run; use CloudLab or AWS if the laptop does not fit; run long jobs in tmux or nohup on a machine that does not sleep.

=== Page 58 ===
Ten pitfalls and how to avoid them:
- P1 Blindly trusting claims: ask for evidence; check one case.
- P2 Losing track: small steps; read the diff; commit.
- P3 Long sessions lose context: new session per task; notes in files.
- P4 Stacking changes: one change per run versus a baseline.
- P5 Parallel sessions collide: one worktree and branch per session.
- P6 Destructive commands: commit first; deny rm -rf and resets.
- P7 Leaked secrets: keys in env vars, never in prompts.
- P8 Reading one noisy run: run several times; compare the spread.
- P9 Venting instead of steering: paste the error; ask for a diagnosis.
- P10 Platform issues and laptop sleep: check requirements; run jobs in tmux.

=== Page 59 ===
Harder assignments, more pitfalls (same 58 students in each assignment; A2 share of errors caught not reported):
- Average pitfalls per student: 1.3 / 3.4 / 5.0.
- Stacked changes: 0% / 47% / 78%.
- Decided on one noisy run: 0% / 48% / 66%.
- Share of agent errors students caught: 61% (A1), 33% (A3).
(Note: these stacking / one-run shares differ from p.48 and p.52; the slides do not explain the difference — possibly different definitions. Do not mix the two.)

=== Page 60 === (no extractable text)

=== Page 61 ===
Claude Code best practice, a good iteration loop: (1) start with a simple baseline (do not start with pi or dsh); (2) create one hypothesis; (3) make one change; (4) run local tests or the leaderboard test; (5) repeat at least once; (6) record a version if verified. Stay in charge: work step by step and verify before moving on. Testing rigor matters.

=== Page 62 ===
Towards effective use of agents: an experimental feedback platform, https://how-i-used-claude.cs2680.com. Feedback welcome.

=== Page 63 === (footer only)
=== Page 64 === (footer only)

=== Page 65 ===
"AI is a tool everyone has to MASTER": reflection prompts — where did things break or fail, where did you waste time? How can you improve quality, effectiveness, productivity? Was the prompt too vague, or the project too large to hand off? Should the prompt be longer and more detailed? Are important things missing? Are there better ways to use agents? Platform: https://how-i-used-claude.cs2680.com (work in progress).

=== Page 66 ===
Section: "How you compare with your classmates."

=== Page 67 ===
Section: "Visibility into your Claude Code usage."

=== Page 68 ===
Section: "Semi-personalized tips for everyone."

=== Page 69 ===
Section: "Course-staff feedback across assignments."

=== Page 70 ===
"Everyone has an agentability portrait": a personal profile that changes with each new assignment.

=== Page 71 ===
"Everyone is different in the class! Have fun!": invites feedback at https://how-i-used-claude.cs2680.com.

=== Page 72 ===
Next class: GPU programming; LLM serving basics III: scheduling, paging and parallelism.

TOTAL PAGES: 72

## Readings

課程網站 11/02 這一堂沒有列 readings（2026-11-06 查）。
