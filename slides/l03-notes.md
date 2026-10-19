# L03 slides 逐頁筆記

- 來源：https://cs2680.com/slides/3_agent_use_2.pdf
- 頁數：72（PDF 檢視器的頁數，封面 = 1）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。

注意：slide 右下角的 footer 編號和 PDF 頁數不同。封面的 footer 是 2，而且 footer 跳過 21、37、46、54–60。每一頁下面都標了 `footer: N`，引用時用 Page 標題裡的 PDF 頁數（和 docs/l03.html 現有的 `#page=N` 連結一致）。

=== Page 1 ===
(footer: 2)
Cover. "Modern AI Systems: Agents and System Optimizations." Presenter: Juncheng Yang. Lecture title: "Agent From a User's Perspective II: Multi-agent and Best Practice." Harvard Madsys, course.agentic-system.org.

=== Page 2 ===
(footer: 3)
Update and Reminder.
- Assignment 1 is due.
- Sign up for Assignment 1 sharing.
- Add the instructor and TFs as collaborators on your repo.
- New TF: Charles Wang.

=== Page 3 ===
(footer: 4)
Recap.
- Agent loops.
- State management: context is working memory; each user prompt, LLM response and tool-call result is appended. Agent memory persists across sessions: CLAUDE.md (AGENTS.md) and auto memory.
- Tools: built-in tools, plus ways to extend Claude Code: skill, MCP, hook, plugin.

=== Page 4 ===
(footer: 5)
Plan for Today.
- Case studies: Superpowers and Caveman.
- Becoming a 100x researcher / engineer with multiple agents.
- Programming / Software 3.0: how programming has evolved.
- How people use OpenAI Codex: two reports, June 2026 and September 2026.

=== Page 5 ===
(footer: 6)
Case Study: Superpowers. Subtitle: a software-development plugin.
- Repo: https://github.com/obra/superpowers
- Install: `/plugin install superpowers@claude-plugins-official`

=== Page 6 ===
(footer: 7)
Same Model, Different Workflow.
- Six stages, grouped: PLAN = (1) clarify the problem, (2) approve a design, (3) write a detailed plan. BUILD = (4) test-driven build. SHIP = (5) review and verify, (6) finish or integrate the branch.
- Stage 0 is the human typing the prompt.
- Default workflow for comparison: feature request -> start coding -> fix by iteration.
- Key point: both agents share the same model and tools. Only the instructions differ.
[Figure: Swimlane diagram. Top lane is the Superpowers workflow: human prompt, then six stages under PLAN / BUILD / SHIP. Bottom lane is DEFAULT: feature request -> coding -> iterative fixing.]

=== Page 7 ===
(footer: 8)
Nine Skills in Superpowers (marked OPTIONAL extra reading). Table, skill | responsibility:
- using-superpowers | rules for discovering and invoking skills
- brainstorming | turns a request into an approved design
- writing-plans | decomposes the design into concrete tasks
- using-git-worktrees | creates an isolated workspace
- test-driven-development | enforces red, green, refactor
- systematic-debugging | finds root causes before proposing fixes
- requesting-code-review | reviews implementation against the plan
- verification-before-completion | requires evidence before reporting success
- finishing-a-development-branch | merge, pull request, retention, or cleanup

=== Page 8 ===
(footer: 9)
Superpowers Architecture.
- Repo layout:
  ```
  superpowers/
  ├── .claude-plugin/     plugin.json
  ├── hooks/              hooks.json, session-start
  ├── skills/
  │   ├── using-superpowers/
  │   ├── brainstorming/
  │   ├── writing-plans/
  │   └── test-driven-development/
  └── tests/
  ```
- Component map: the plugin contains plugin metadata, a session hook, and a skill library; together they shape agent behavior.
- Takeaway: the plugin is the distribution container. Skills and hooks supply the behavior.
[Figure: Repo tree on the left; component diagram on the right with the plugin at center linked to plugin metadata, session hook, skill library, all feeding "agent behavior".]

=== Page 9 ===
(footer: 10)
Anatomy of a Skill.
- Directory `skills/brainstorming/` contains `SKILL.md`, `visual-companion.md`, and a `scripts/` folder.
- Simplified SKILL.md:
  ```
  ---
  name: brainstorming
  description: Use before creative work.
  ---
  ## Workflow
  1. Inspect the project
  2. Classify the scope
  3. Clarify requirements
  4. Compare approaches
  5. Present a design
  6. Wait for user approval
  7. Invoke writing-plans
  ```
- Front matter is metadata. The body is the procedure the agent follows.
[Figure: File tree of the brainstorming skill folder beside the SKILL.md excerpt.]

=== Page 10 ===
(footer: 11)
What a SKILL.md Contains. Table, component | function:
- name | stable identifier
- description | when the skill applies
- Instructions | the procedure to follow
- Checkpoints | approval before proceeding
- References | detail loaded only when needed
- Scripts | deterministic operations
What a process skill can define: entry conditions; required actions; prohibited actions; human approval gates; verification requirements; the next applicable skill.
- Takeaway: each skill guides behavior and can name its successor.
[Figure: Two columns: the six components on the left, the process-skill definitions on the right.]

=== Page 11 ===
(footer: 12)
Why Skills Alone Are Not Enough.
- Installing a skill makes it available, but availability does not guarantee the agent will check it.
- `hooks/hooks.json`:
  ```json
  {
    "hooks": {
      "SessionStart": [{
        "matcher": "startup|clear|compact",
        "hooks": [{ "type": "command",
          "command": "run-hook.cmd",
          "async": false }]
      }] } }
  ```
- What the hook guarantees: deterministic timing in every session; runs before the agent acts; re-runs after clear and compaction.

=== Page 12 ===
(footer: 13)
The Session-Start Script (OPTIONAL extra reading). Simplified `hooks/session-start`:
```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(plugin_root)"
skill="$ROOT/skills/using-superpowers/SKILL.md"
content="$(cat "$skill")"
printf '{"hookSpecificOutput": {
  "hookEventName": "SessionStart",
  "additionalContext": "%s" }}' \
  "$(escape_json "$content")"
```
Steps: (1) locate the installed plugin; (2) read the bootstrap SKILL.md (using-superpowers); (3) escape the Markdown for JSON; (4) return it as `additionalContext`; (5) Claude Code adds it to context.

=== Page 13 ===
(footer: 14)
End-to-End Walkthrough. Example request: "Add authentication."
1. Claude Code starts the session.
2. The hook reads the bootstrap skill.
3. The agent receives the selection policy.
4. User sends "Add authentication."
5. The agent loads brainstorming and clarifies.
6. User approves the design.
7. The agent loads writing-plans and produces an implementation plan.
- Later stages: isolated worktree, test-driven build, code review, verification, branch integration.

=== Page 14 ===
(footer: 15)
Design Lessons From Superpowers (OPTIONAL extra reading). Table, design question | Superpowers' answer:
- How should complex behavior be represented? | Small, composable skills
- How does the agent remember to use them? | A bootstrap skill via a session hook
- How is context kept manageable? | Load task skills only when relevant
- How do stages coordinate? | Each skill names its gates and successor
- How do users install the system? | Package everything as a plugin
- Does every plugin need commands or MCP? | No. Add them only when needed

=== Page 15 ===
(footer: 16)
Caveman case study (intro). Subtitle: five extension mechanisms, plus a local proxy.
- Install:
  ```
  claude plugin marketplace add JuliusBrussee/caveman
  claude plugin install caveman@caveman
  ```
- The five mechanisms (detailed on later pages): skills, commands, hooks, MCP, plugin packaging; plus the local proxy.

=== Page 16 ===
(footer: 17)
Why Compress an Agent's Tokens?
- Context fills up: logs, diffs, and tool output crowd out the actual work.
- Every turn costs: tokens are paid for and waited on, in both directions.
- Compaction loses detail: trimming context late drops what mattered.
- BEFORE (786 lines of test output):
  ```
  $ npm test
  FAIL src/api/client.test.ts
    ● client › retries on 5xx
      connect ETIMEDOUT 10.0.3.8:443
      at client.ts:88
  … 776 more lines …
  3 failed, 214 passed
  ```
- AFTER (what the model reads): `3 tests fail: ETIMEDOUT at client.ts:88`
- Takeaway: compress in both directions, and keep the original available for retrieval.
[Figure: Before/after comparison. Left block is the long noisy test log; right block is the single summary line that keeps the error and location.]

=== Page 17 ===
(footer: 18)
Caveman Compresses Tokens in Two Directions.
- Input path: agent input (logs, tool results, diffs, files) passes through the local proxy and engine before reaching the model.
- Output path: agent output passes through the response skill, injected earlier in context, before the user reads it.
- The skill changes how the model writes. The proxy changes what the model reads.
- Reported: 65% fewer output tokens. The skill itself adds input tokens, so whole-session savings are smaller.
- Example prompt: `/caveman ultra`, then "Run the tests and explain the failure."
[Figure: Model in the center. Left: agent input flows through local proxy and engine into the model. Right: agent output flows through the response skill to the user.]

=== Page 18 ===
(footer: 19)
Walk Through an Example (OPTIONAL extra reading). Prompt: `/caveman ultra`, then "Run the tests and explain the failure."
1. The hook stores ultra mode.
2. The hook injects the concise-response reminder.
3. The agent executes the command (generated by the LLM).
4. Caveman (proxy) compresses the noisy test output.
5. The model receives the reduced context.
6. The model returns a concise diagnosis.
7. MCP retrieves the original on demand.

=== Page 19 ===
(footer: 20)
Plugin Packaging.
- Repo structure:
  ```
  caveman/
  ├─ .claude-plugin/plugin.json
  ├─ skills/   caveman, -commit, -review, -compress, -stats
  ├─ commands/
  ├─ src/hooks/
  ├─ mcp/
  ├─ proxy/
  ├─ engine/
  └─ agents/
  ```
- Plugin manifest:
  ```json
  {
    "name": "caveman",
    "hooks": {
      "SessionStart": ["caveman-activate.js"],
      "UserPromptSubmit": ["caveman-mode-tracker.js"]
    }
  }
  ```
[Figure: File tree of the caveman plugin: manifest, skills, commands, hook source, MCP server, proxy, engine, agents.]

=== Page 20 ===
(footer: 22)
The Response Skill Makes Output Less Verbose.
- File: `SKILLS/CAVEMAN/SKILL.md`:
  ```
  ---
  name: caveman
  description: Compressed mode
  ---
  # Caveman response mode
  Preserve: technical terms, commands, paths, code, errors, numbers, units, negation
  Remove: filler, repetition, pleasantries, hedging
  Short sentences. Active voice.
  ```
- Preserve: technical terms, commands, paths, code, errors, numbers, units, negation. Remove: filler, repetition, pleasantries, hedging. Short sentences, active voice.
- Takeaway: this changes how the agent communicates (not what it reads).

=== Page 21 ===
(footer: 23)
Commands Provide Explicit User Control.
- `/caveman` default full mode; `/caveman ultra` maximum compression; `/caveman off` deactivate.
- `/caveman-commit` concise commit message; `/caveman-review` concise review findings; `/caveman-compress` compress a memory file; `/caveman-stats` session token statistics; `/caveman-help` available operations.
- `COMMANDS/CAVEMAN.md`:
  ```
  ---
  description: Activate Caveman mode
  argument-hint: [lite|full|ultra|off]
  ---
  Activate Caveman mode: $ARGUMENTS
  If no level is supplied, use full.
  If off, deactivate.
  ```
- `$ARGUMENTS` receives the level typed by the user (lite, full, ultra, off). No level -> full.

=== Page 22 ===
(footer: 24)
Hooks Make a Prompt-Time Choice Persistent.
- SessionStart runs `caveman-activate.js`: decides the mode for this session and stores it safely; injects the rules as hidden context; restores the rules after compaction; cleans old state and offers a status line.
- UserPromptSubmit runs `caveman-mode-tracker.js`: inspects every user prompt; detects `/caveman ultra` and phrases like "normal mode"; updates the session's mode and restores it after focused operations.
- Config:
  ```
  "hooks": {
   "SessionStart": ["node caveman-activate.js"],
   "UserPromptSubmit": ["node caveman-mode-tracker.js"]
  }
  ```
- Key distinction: SessionStart initializes behavior; UserPromptSubmit detects mode changes mid-conversation.
[Figure: Two columns, SessionStart box (activate script) and UserPromptSubmit box (mode tracker), with the config code block below.]

=== Page 23 ===
(footer: 25)
MCP Exposes Compression as Callable Tools. Five tools:
- `caveman_compress`: compression plus a recovery handle
- `caveman_retrieve`: byte-exact original
- `caveman_stats`: compression statistics
- `caveman_toon_encode`: JSON -> TOON
- `caveman_toon_decode`: TOON -> JSON
- Config:
  ```
  {"mcpServers": {
   "caveman": {
   "command": "npx",
   "args": ["-y","caveman-mcp"]
  ```
- Example tool result:
  ```
  "compressed": "3 tests fail. Root error: timeout.",
  "ratio": 0.72,
  "recovery_handle": "ccr_abc123"
  ```
- The recovery handle lets the agent fetch the original later with `caveman_retrieve`.

=== Page 24 ===
(footer: 26)
The Proxy Compresses What the Model Reads.
- Path: coding agent -> local Caveman proxy -> model provider.
- Type-aware compression, what is kept per type:
  - Logs | errors, stack traces, head + tail
  - Code | imports, signatures, types, bodies
  - Diffs | file + hunk headers, changed lines
  - JSON | keys, structure, error subtrees
  - Search | high-value matches, diagnostics
  - HTML / text | headings, relevant sections
- Proxy vs MCP: the proxy intercepts every request; MCP runs only when called. The proxy sits between agent and provider; MCP sits beside it. The proxy changes context; MCP cannot.
- Note: hooks intercept requests but cannot transparently rewrite the request to the LLM, so a proxy is needed. With your own harness you can do this directly.
[Figure: Three boxes left to right: "Coding agent" -> "Local Caveman proxy" -> "Model provider".]

=== Page 25 ===
(footer: 27)
How Capabilities Are Used in Caveman. Table, capability | role:
- Skills | concise styles and focused workflows
- Hooks | activate, track, and reinforce the mode
- Commands | select modes and request operations
- MCP | compression, retrieval, stats, and encoding
- Plugin | packages the Claude Code integration
- Local proxy | intercepts provider requests
Row labels: PACKAGE = the Caveman plugin is one installation and update unit. MECHANISMS = skills, commands, hooks, MCP server. STATE + ENGINE = session mode state and the compression engine. INTERCEPT = local proxy between the agent and the model provider.

=== Page 26 ===
(footer: 28)
Become a 100x Engineer With Multiple Long-Running Agents. Section opener.
- Four options: Parallel Agents by Hand, Subagent, Agent Team, Dynamic Workflow.
- Tagline: "Agents fan out in parallel. So does the invoice."
- Sequence: 1 · Show up; 2 · Stay awake here; then "Done before lunch."
- Guiding question: "How do you finish the assignments in two hours?"
[Figure: Four option labels, then a three-step progression: show up, stay awake, done before lunch.]

=== Page 27 ===
(footer: 29)
Three Axes of Scaling.
- Parallel agents (breadth): multiple independent tasks, each in an isolated working tree. Buys throughput (wall-clock time), not answer quality.
- Subagents (breadth and depth): delegate a bounded task to a fresh context and get a summary back. Buys throughput and focus; the parent never sees the intermediate mess.
- Long-running agent (duration): carry a larger job across many steps. Buys scope: more work with less intervention.
- Agent teams and dynamic workflows combine these axes.

=== Page 28 ===
(footer: 30)
Parallel Agents by Hand.
- One task per session, each in its own git worktree (a separate working directory and branch that shares the repo's history).
- Terminal 1: `claude -w feature-payments` builds the feature on its own branch.
- Terminal 2: `claude -w bugfix-auth` fixes the bug, untouched by the first.
- Edits in one session never touch files in another. No stashing, no second clone. In the desktop app every new session gets a worktree automatically.

=== Page 29 ===
(footer: 31)
Git Worktree: One Repo, Many Working Directories.
- One shared repo: `.git` holds history, branches, objects, remotes.
- `../repo-main` | branch `main` | Agent 1: review
- `../feat-auth` | branch `feature/auth` | Agent 2: build
- `../fix-flaky` | branch `fix/flaky-test` | Agent 3: debug
- Takeaway: one shared history, three checkouts, no branch switching, no stashing.
[Figure: "One repository" box with `.git` on top; three arrows down to three directory boxes, each labeled with path, branch and agent.]

=== Page 30 ===
(footer: 32)
Where Hand-Run Parallelism Stops.
- A few sessions is a productivity win; twenty sessions needs "a clone of yourself."
- You hold the plan: every hand-off and next step lives in your head.
- Sessions cannot see each other: findings move only if you carry them across.
- You reconcile the branches: merge order and conflicts are yours.
- It does not repeat: nothing about the run is written down to rerun.
- Comparison: 3 sessions = "you can hold the plan"; 20 sessions = "you need a clone".
[Figure: Two stacks, "3 sessions" operated by you alone, "20 sessions" operated by you + a clone.]

=== Page 31 ===
(footer: 33)
Subagents: Why? A subagent is a specialized assistant with its own context window, tools, and permissions.
- Preserve context: logs, search results, file dumps stay out of the main conversation.
- Enforce constraints: limit which tools a subagent may use and which model runs it.
- Reuse anywhere: focused prompts for a domain, shared across projects and teams.
- Parallelization: independent subtasks run concurrently; the slowest one sets the total time. Example: style-checker, security-scanner, test-coverage run at once.
- Control costs: route tasks to faster, cheaper models like Haiku, via `model: haiku` in the subagent frontmatter.
- Reference: code.claude.com/docs/en/sub-agents

=== Page 32 ===
(footer: 34)
Built-In Subagents (Claude delegates to these automatically).
- Explore: read-only codebase search; Write and Edit denied; thoroughness set per call.
- Plan: research during plan mode, so exploration stays out of the main window.
- General-purpose: complex multi-step work needing both exploration and action.
- Explore and Plan skip CLAUDE.md and git status to stay fast and cheap.

=== Page 33 ===
(footer: 35)
Defining a Subagent. A Markdown file with YAML frontmatter; the body becomes the system prompt.
- `.claude/agents/code-reviewer.md`:
  ```
  ---
  name: code-reviewer
  description: Reviews code for quality
  tools: Read, Glob, Grep
  model: sonnet
  ---
  You are a code reviewer. Analyze the
  code and give actionable feedback.
  ```
- `.claude/agents/`: project scope; check into version control so the team shares it.
- `~/.claude/agents/`: user scope; available across all your projects.

=== Page 34 ===
(footer: 36)
Defining a Nested Subagent.
- Frontmatter:
  ```
  ---
  name: my-orchestrator
  tools: Read, Grep, Agent
  model: claude-sonnet-5-0
  ---
  ```
- `Agent` must appear in `tools` before a subagent can spawn children. The parent subagent spawns each child with an Agent tool call.
- Up to 5 levels of nesting allowed; 2 to 3 levels is the sweet spot.
[Figure: Tree: "Parent subagent" on top; two arrows labeled "Agent tool call" down to "Child subagent 1" and "Child subagent 2".]

=== Page 35 ===
(footer: 38)
Multi-Level Subagents: A Common Pattern.
- Level 0: Main agent, owns the plan.
- Level 1: Implementer subagent; Debugging subagent; Code-review subagent.
- Level 2: Test-writer subagent; Verification subagent. (The text layer does not say which Level 1 node each Level 2 node hangs under.)
- "Every level starts with fresh context and returns only a summary."
[Figure: Three-level tree: main agent at top, three Level 1 subagents below it, two Level 2 subagents below those; delegation arrows down, summaries return up.]

=== Page 36 ===
(footer: 39)
Work With Subagents. Automatic delegation happens on its own; escalate to explicit control when it doesn't trigger. Three ways, in order of increasing control:
1. Natural language (scope: ONE-OFF). Name the subagent in the prompt, e.g. "Use the test-runner subagent to fix tests." Claude decides whether to delegate.
2. @-mention (scope: ONE TASK). e.g. "@agent-code-reviewer look at auth changes." The subagent is guaranteed to run.
3. `--agent` flag (scope: WHOLE SESSION). `claude --agent code-reviewer`. The session adopts the subagent's prompt, tools, and model.
[Figure: Three stacked boxes with increasing control, each showing an example prompt and its scope.]

=== Page 37 ===
(footer: 40)
Subagent, or Main Conversation? A subagent starts fresh: it sees no history and pays a latency cost to gather context.
- Keep in the main conversation: iterative back-and-forth; phases that share context; quick, targeted changes; cases where latency matters.
- Delegate to a subagent: verbose output you won't reuse; tool or permission restrictions; self-contained work that returns a summary; parallel, independent work; simple work that can go to a small model.
- For a reusable workflow that runs in the main context, use a Skill instead.

=== Page 38 ===
(footer: 41)
Agent Teams. Several Claude Code sessions work together: one lead and several teammates.
- Review: teammates probe different angles, then challenge each other's findings.
- Independent modules: each teammate owns a separate piece without stepping on the others.
- Debugging: competing hypotheses tested in parallel converge faster.
- Cross-layer: frontend, backend, and tests, each owned by a teammate.
- Caveats: coordination overhead and token cost scale with team size. Sequential tasks, same-file edits, or heavy dependencies are better handled by one session or by subagents.
- Status: experimental and off by default. Docs: code.claude.com/docs/en/agent-teams

=== Page 39 ===
(footer: 42)
How a Team Is Wired. Four parts; teammates talk to each other directly.
- Team lead: the main session; spawns teammates, coordinates work, synthesizes results.
- Teammates: separate Claude Code instances, each with its own context window.
- Task list: shared work items that teammates claim and mark complete.
- Mailbox: a JSON inbox per agent.
- Teammates do not inherit your conversation. They load CLAUDE.md and skills automatically, so task details must go in the spawn prompt.

=== Page 40 ===
(footer: 43)
Agent Team vs Subagent.
- Subagents: the main agent sends work to subagents; results report back to it.
- Agent teams: the team lead shares a task list; teammates claim tasks and message each other.
[Figure: Two diagrams. Top "Subagents": main agent with arrows down to three subagent boxes, each returning "Result" to the main agent. Bottom "Agent teams": main agent (team lead) above a shared task list, three teammate boxes below with lateral arrows, label "Claim tasks and message each other".]

=== Page 41 ===
(footer: 44)
Subagents vs Agent Teams. Table, dimension | subagents | agent teams:
- Context | own window; result returns to caller | own window; independent
- Communication | back to the caller only | teammate to teammate
- Coordination | lead manages the work | shared task list
- Best for | result-only tasks | work that needs discussion
- Token cost | lower | higher
- Takeaway: teams cost more, so use them only when the work needs discussion.

=== Page 42 ===
(footer: 45)
Subagents vs Agent Teams (repeat). Identical table and takeaway to Page 41; only the footer number differs. Looks like a duplicate slide.

=== Page 43 ===
(footer: 47)
Dynamic Workflow. A JavaScript script that orchestrates many subagents in the background.
- Use it when a task needs more agents than one conversation can coordinate. Examples: codebase-wide bug sweep; a 500-file migration; research cross-checked; a plan from several angles.
- Two ways to start one: type "ultracode" in your prompt ("Type it in your prompt"), or `/effort ultracode` ("Let Claude decide for you"). The text layer does not hard-link the two labels to the two commands; this pairing is by order on the slide.
- Both routes spawn many subagents: plan, design, implement, review.

=== Page 44 ===
(footer: 48)
Long-Running Agents: /goal. Hand over a verifiable end state; Claude keeps working until it holds.
- Example: `/goal "npm run lint exits with zero errors"`
- Define done: a condition Claude can test (tests pass, zero lint errors).
- Self-checks: an evaluator rechecks the condition after each attempt and sends Claude back in if not met.
- Stops itself: ends when the goal is met or when `--max-tries` runs out.
- "All integration tests pass" is verifiable; "refactor the code" is not.

=== Page 45 ===
(footer: 49)
Long-Running Agents: /loop. Re-run a prompt on a schedule until you stop it.
- Example: `/loop 5m "check CI, fix whatever broke"`
- A trigger, not a test: you set the interval; the same prompt runs each time.
- You end it: press Esc while it waits between runs.
- Default prompt: put one in `.claude/loop.md`.
- Contrast: `/goal` stops when the condition holds; `/loop` stops when you ask.

=== Page 46 ===
(footer: 50)
Summary. Four ways to amplify with multiple agents, and two ways to keep one agent running.
- One agent, for longer: `/goal` runs until a verifiable end state holds; `/loop` re-runs on a schedule until you stop it.
- More agents at once: parallel agents by hand (you reconcile them yourself); subagents (Claude delegates, results come back to it); agent teams (a lead supervises peers over a shared list); workflows (a script holds the plan, not the chat).
[Figure: Two groups: "One agent, for longer" (/goal, /loop) and "More agents at once" (parallel by hand, subagents, agent teams, workflows).]

=== Page 47 ===
(footer: 51)
Agent Team Example: Sixteen Agents Built a C Compiler (OPTIONAL extra reading). A Rust C compiler that builds the Linux kernel, by 16 agents over about two weeks.
- Scale: 16 agents in parallel; about 2,000 sessions over two weeks; 2B input and 140M output tokens; just under $20,000 in API cost.
- Result: about 100,000 lines of code; Linux 6.9 builds on x86, ARM, and RISC-V; builds/runs QEMU, FFmpeg, Postgres, Redis, Doom; about 99% pass rate on major test suites.
- Source: anthropic.com/engineering/building-c-compiler

=== Page 48 ===
(footer: 52)
How the Sixteen Agents Coordinated (OPTIONAL extra reading). Orchestration used plain infrastructure: containers, Git, text files.
- Each agent ran in an isolated container and Git checkout.
- Tasks were claimed through simple lock files.
- Git served as the coordination and integration layer.
- Fresh sessions read progress docs to regain context.
- Specialist agents handled docs, performance, quality, and deduplication.
- Automated tests gave agents a progress signal.

=== Page 49 ===
(footer: 53)
Git as the Coordination Layer (OPTIONAL extra reading). No chat channel, no manager agent; agents coordinate through shared Git state.
- Loop: (1) read the repo: clone, scan docs and logs; (2) claim a task: create a lock file in `current_tasks/`; (3) implement and test in its own container; (4) merge, push, unlock: pull everyone else's changes first. Repeat.
- Agents pick the next obvious task themselves; Git settles duplicate claims.
- Conflicts settle themselves: if a task is claimed twice, one agent moves on.
- Artifacts carry context: READMEs, progress docs, and CI failures brief new sessions.
[Figure: Circular flow of four boxes: Read the repo -> Claim a task (lock file in current_tasks/) -> Implement and test (own container) -> Merge, push, unlock (pull others first) -> back to start.]

=== Page 50 ===
(footer: 61)
Successful but Not Fully (OPTIONAL extra reading). Subtitle: "Agent is not yet perfect, more work ahead for you!" Limitations of the 16-agent C compiler project:
- Merge conflicts were frequent.
- Parallelism stopped helping once every agent hit the same kernel failure.
- It still relied on GCC for part of 16-bit x86.
- Generated code was less efficient than GCC output.

=== Page 51 ===
(footer: 62)
Programming / Software 3.0. Section divider, no other content.

=== Page 52 ===
(footer: 63)
Programming 3.0. Three pipelines:
- Programming 1.0 (programming hardware): Human -> explicit machine instructions / assembly -> Hardware.
- Programming 2.0 (programming language): Human -> programming language -> Compiler -> machine instructions -> Hardware.
- Programming 3.0 (expressing goal): Human -> natural language -> Agent -> programming language -> machine instructions -> Hardware.
- Annotations on the 3.0 row: "Higher productivity" and "More uncertainty."
- Note: "Programming 3.0" is the lecturer's own term; it differs from Andrej Karpathy's "Software 3.0" (next page).
[Figure: Three horizontal pipelines, each from a Human box to a Hardware box; 1.0 has one intermediate box, 2.0 adds a language and a compiler, 3.0 inserts an agent between natural language and the programming language.]

=== Page 53 ===
(footer: 64)
Software 3.0 (Andrej Karpathy's framing).
- Software 1.0: human code -> computer.
- Software 2.0: human data -> optimizer -> neural network.
- Software 3.0: human language / context -> LLM -> action.
- Table, paradigm | what is the program? | how to create it:
  - 1.0 | source code | write Python / C++
  - 2.0 | neural-network weights | collect data + optimize
  - 3.0 (Andrej Karpathy) | LLM prompts | natural language
- Takeaway: "Knowing where to draw the boundary between 1.0, 2.0 and 3.0 is an important engineering skill."
- Source: "Software Is Changing (Again)" (YouTube).
[Figure: Three stacked pipeline rows for Software 1.0, 2.0, 3.0.]

=== Page 54 ===
(footer: 65)
Uncertainty in Programming 3.0. Single message: "Uncertainty becomes the core theme, and you should learn to live with it!"

=== Page 55 ===
(footer: 66)
Is Uncertainty New? Table, columns Hardware | Environment | Software:
- Programming 3.0 adds | GPU compute: nondeterministic kernels, floating-point variance | Interaction at codegen: it touches the environment as it writes | Compiler, model: different kernels, sampling
- Programming 2.0 already had | Architecture: 32-bit vs 64-bit, endianness | Concurrency, unreliable networks | Compiler versions, dependency drift
- How 2.0 solves it | Fixed-width types, cross-compilation, virtualization | Memory consistency model, idempotent APIs | Comprehensive tests before upgrade
- Takeaway: "The same source code != same output happened a long time ago."

=== Page 56 ===
(footer: 67)
A Bit More Uncertainty: from intent to result.
- Programming 1.0 / 2.0: Human (PM) -> need -> Programmer -> program runs in env + memory -> program result.
- Programming 3.0: Human -> need -> LLM agent -> program runs in env + memory -> program result.
- Annotations on the diagram: "Ignored (but exists)"; "Formal verification"; "Discussed in prev slide"; "Ambiguous input due to a single prompt"; "More research needed." The text layer does not map each annotation to a specific arrow; the sense is that the human->need step was previously ignored but exists, programmer->program is where formal verification lives, env/memory uncertainty is the previous slide, and the single-prompt ambiguity plus the LLM-agent step are the new research gaps.
[Figure: Two horizontal chains; the bottom chain replaces "Programmer" with "LLM agent" and keeps the same env/memory and result boxes.]

=== Page 57 ===
(footer: 68)
Live With Uncertainty. Four sources:
- Natural-language semantic uncertainty.
- Retrieval / context retrieval drift: index updates, chunking, context truncation.
- Model generation probabilistic variability: (1) sampling; (2) software and hardware nondeterminism.
- Agent / tool loop: trajectory and environment nondeterminism, tool failure, environment change.
- Bottom note: a generated program is usually deterministic once generated, unless it calls models or tools at runtime.

=== Page 58 ===
(footer: 69)
Best Practices for Programming / Software 3.0.
- 1 · DEFINE: state assumptions up front; have the model confirm anything ambiguous before it executes.
- 2 · CONTROL: separate proposal from execution (agents propose plans; validate before anything commits). Manage context explicitly (own memory, provenance and retrieval; expire stale information). Specify outcomes, not prompts (requirements, invariants, constraints, acceptance tests).
- 3 · VERIFY & GOVERN: tighten the generate-verify loop (cheap, frequent checks beat one expensive review at the end). Measure one level deeper (create tests, measure multiple metrics, use synthetic workloads you can reason about).

=== Page 59 ===
(footer: 70)
Untitled text slide. Two principles:
- "Do not expect the agent to be deterministic; make the surrounding system dependable."
- "Match autonomy to risk: the more autonomy, the higher the uncertainty and risk."

=== Page 60 ===
(footer: 71)
Evidence From the Field. Section divider. Two evidence sources: evidence from Codex (June 2026); OpenAI employee usage (September 2026).

=== Page 61 ===
(footer: 72)
From Conversation to Delegation. Source: "The Shift to Agentic AI: Evidence from Codex."
- Conversational AI: human asks a question -> model answers -> human stays in the loop -> human executes the work. Callout: "The human is the executor."
- Agentic AI (Codex): human delegates a task -> agent plans, calls tools, edits files, runs commands -> artifact or action delivered -> human reviews and integrates. Callout: "The human reviews and integrates."
- Adoption: active Codex users grew more than 5x in the first half of 2026.
- Used Codex in the last 28 days: individual users < 1%; organizational users 17.3%; OpenAI workers nearly all.
[Figure: Two side-by-side vertical four-step flows, Conversational AI on the left and Agentic AI on the right.]

=== Page 62 ===
(footer: 73)
Delegated Tasks Are Getting Much Bigger. Share of delegated tasks at or above a human-time threshold, December 2025 vs May 2026.
- Task >= 1 human-hour: December 2025 = 35.4%; May 2026 = 70.2%.
- Task >= 8 human-hours: December 2025 = 2.1%; May 2026 = 25.6%.
- Headline callout: "12x rise in users tackling full-day tasks" (25.6 / 2.1 is about 12.2x).
[Figure: Grouped bar chart. Y-axis 0% to 80% in 10% steps. X-axis categories "Task >= 1 human-hour" and "Task >= 8 human-hours". Legend: December 2025, May 2026.]

=== Page 63 ===
(footer: 74)
One Human, Many Agents. The human's role shifts to planner, delegator, monitor, reviewer, integrator.
- Diagram: one human coordinates Agent A (build feature), Agent B (run analysis), Agent C (debug + test); loop labeled "Review · integrate · re-delegate."
- Stats (June 2026): 28.6% of OpenAI users ran 5+ agents at once in a week. Median OpenAI employee: about 2.5 agent-hours per day. 99th percentile: about 71 agent-hours per day, up 88% since April.
[Figure: Human box fanning out to three agent boxes with a feedback loop back to the human.]

=== Page 64 ===
(footer: 75)
Agentic Workdays Now Far Exceed Human Researchers. September 2026.
- "Before June 2026 agent runtime trailed human labor, now agents do 3.14x more work than humans."
- "Most researchers have 4+ concurrent workflows (not shown)."
[Figure: Chart comparing agent runtime with human labor over time. Axis labels and values are not in the text layer; the 3.14x figure comes from the slide text.]

=== Page 65 ===
(footer: 76)
Engineers Are Shipping Almost 8x Faster. Title only; the rest is a chart.
[Figure: Chart supporting the 8x throughput claim. Axis labels and values are not extractable from the text layer.]

=== Page 66 ===
(footer: 77)
Agents Solve Increasingly More Complex Tasks. Subtitle: "But Human Intervention is Still Needed." Title and subtitle only.
[Figure: Chart of task complexity over time with continued human intervention. Labels and values are not extractable from the text layer.]

=== Page 67 ===
(footer: 78)
Coding Agents Are Reshaping Daily Work for OpenAI Researchers. Subtitle: "Research acceleration: The view inside OpenAI," September 2026. Title and subtitle only.
[Figure: Visualization from the OpenAI report; content not extractable from the text layer.]

=== Page 68 ===
(footer: 79)
The Delegation Ladder. Five levels:
1. Chatbot: AI answers; the human does the work.
2. Assistant: human and AI work on the task together.
3. Agent: the human delegates a whole unit of work.
4. Multi-agent worker: the human coordinates several agents.
5. Systematized workflows: skills and agents run processes.
- OpenAI's workforce sits near the bottom of the ladder.

=== Page 69 ===
(footer: 80)
Next Class: Agent design I. Find a TF to get your participation score.

=== Page 70 ===
(footer: 81)
Optional Slides. Section divider, no content.

=== Page 71 ===
(footer: 82)
Beyond Claude Code. Source: "State of CLI Coding Agents, Mid-2026" (July 2026). Four groups:
- Model labs (model + harness in one): Claude Code, Codex CLI, Antigravity CLI, Grok Build, Mistral Vibe, Kimi Code, Qwen Code.
- Platform CLIs (inside a dev stack): Copilot CLI, Cursor CLI, Amp, Auggie, Droid, Junie CLI, Qoder, CodeBuddy.
- Open source (bring your own key): OpenCode, Crush, Goose, Aider, Cline, Kilo, Continue, OpenHands, Reasonix, Codebuff.
- Minimal cores (small and auditable): Deepseek Harness, Pi, oh-my-pi (Omp), mini-SWE-agent, gptme, Open Interpreter.
[Figure: Grouped map of CLI coding agent names in four boxes.]

=== Page 72 ===
(footer: 83)
How They Differ: Five Axes That Matter. Source: "State of CLI Coding Agents, Mid-2026" (July 2026). Table, axis | examples:
- Open vs closed | Open: Codex CLI, OpenCode, Goose, Cline, Pi. Closed: Claude Code, Copilot CLI, Cursor, Droid, Junie.
- Locked vs BYOK | One vendor: Claude Code, Antigravity CLI, Grok Build. Any endpoint: OpenCode (75+ providers), Kilo (500+ models).
- Sandbox vs prompt | OS sandbox: Codex CLI, Copilot CLI, OpenHands (containers). Permission prompts: Claude Code and most others.
- Local vs cloud | Local-first, no telemetry: Goose, Nanocoder, gptme. Cloud handoff: Copilot CLI, Codex, Mistral Vibe (remote agents).
- Maximal vs minimal | Everything included: Omp (widest feature set), Claude Code. Four tools only: Pi, mini-SWE-agent (about 100 lines of Python).
