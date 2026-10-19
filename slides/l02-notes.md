# L02 slides 逐頁筆記

- 來源：https://cs2680.com/slides/2_agent_use_1.pdf
- 頁數：53（PDF 檢視器的頁數，封面 = 1；與 docs/l02.html 的 data-pages-total 一致）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。
- 頁碼校正：WebFetch 把 slide 右下角的 footer 號碼當頁碼，footer 會跳號（隱藏的 slide）。本檔已換算成 PDF 頁數。 跳過的 footer 號碼：[13, 14, 15, 30, 44, 47, 48]。
  footer → PDF：16–29 → 13–26；31–43 → 27–39；45–46 → 40–41；49–60 → 42–53

=== Page 1 ===
Title: "Modern AI Systems: Agents and System Optimizations." Presenter: Juncheng Yang. Lecture topic: "Agent From a User's Perspective I: How Claude Code Works."

=== Page 2 ===
Section divider with the same lecture title, "Agent From a User's Perspective I: How Claude Code Works." Course site: course.agentic-system.org.

=== Page 3 ===
Title: Schedule update.
- LLM background moves later. Treat the LLM as a "magic reasoning box" for now; internals aren't needed to learn agents.
- More agent, less GPU: more agent content, two extra agent-design lectures, fewer GPU lectures (less overlap with other courses).
- Changes: no mandatory paper presentation; score goes to participation and project; Assignment 1 sharing is now a bonus; a few bonus paper discussions (TBA).

=== Page 4 ===
Title: A few more logistics.
- Hands up = score.
- Labels: OPTIONAL (extra reading, not required); ADVANCED (skim or read on your own).
- New TA: Advaith Ravishankar.
- Participation: ask or answer a question in class for up to 1 point per class; find the TA after class.

=== Page 5 ===
Title: Plan for today.
- How Claude Code works.
- Claude Code as a path from stateless LLM to agent.
- Memory.
- Tools, skills, hooks, plugins.

=== Page 6 ===
Title: What happens when you type a prompt into Claude Code? Prompt for the class; hands up = score.

=== Page 7 ===
Title: The Agentic Loop. Three stages repeat:
1. Gather context (prompt, files, tool results).
2. Generate action (run a tool: bash, read, edit).
3. Run tool (tests, output, re-read state).
- Each step is conditioned on the previous result.
- One user prompt means many model calls and many tool executions, not one request.
- Labels: harness (Claude Code), model, your machine.
[Figure: Circular loop of three stages (gather context, generate action, run tool), with labels for harness, model, and machine.]

=== Page 8 ===
Title: Context Before You Type. Context is already 10+k tokens before the first keystroke. Stack of parts:
- SYSTEM: Claude Code instructions.
- PROJECT: environment.
- MEMORY: persistent project/user notes, CLAUDE.md.
- TOOLS: Read, Edit, Bash, Glob, Grep, Web, Agent.
- SKILLS/MCP: names and descriptions only at start; full text loads when used.
- USER: example prompt "Fix the failing auth test."
[Figure: Stacked blocks of context (system, project, memory, tools, skills/MCP, user prompt) feeding into the window.]

=== Page 9 ===
Title: It Doesn't Send Your Repository. The repo stays on disk; Claude pulls slices on demand.
- Example: Claude asks what it needs, runs Grep("authentication"), and a handful of matching lines enter context.
[Figure: Thousands of files on disk; Claude issues a Grep query; only a small slice returns into context.]

=== Page 10 ===
Title: Model Proposes and then Harness Executes. The model emits a request (e.g., Bash("pytest")); the harness resolves it, checks permissions, and executes on the machine. Stdout/stderr returns as a tool_result into the model's context.
[Figure: Flow: Claude model emits request → Claude Code harness checks and executes → your machine runs pytest → tool_result returns to model.]

=== Page 11 ===
Title: One User Prompt Triggers Many LLM Inferences. One turn alternates inference and tool execution.
- Chain: U (prompt) → M1 (inference) → T1 (tool) → M2 → T2 → … → Mn → A (answer).
- Example session: run pytest → read session.py → grep create_session → edit session.py → pytest, all green.
- Each request depends on the previous inference and tool result.
[Figure: Alternating chain of model inferences (M1 to Mn) and tool calls (T1, T2), ending in an answer A.]

=== Page 12 ===
Title: Permissions Sit Between Intent and Execution. A tool request is a proposal needing approval from you or another model.
- Example request: Bash("rm -rf build/").
- Permission modes: Manual, Accept Edits, Bypass permission, Auto (a small model checks it).
- Outcomes: allowed (runs), ask (you confirm), denied (nothing happens).
[Figure: Claude's request passes a permission layer with modes and three outcomes: allow, ask, deny.]

=== Page 13 ===
Title: Context Grows, Then Gets Compacted. Each step adds tokens (model replies, file contents, command output).
- Compaction: summarize old trajectory; re-inject CLAUDE.md and memory.
- Context management is a key harness design component (next week).
- Typical context size: 1M tokens (Sonnet, Opus, Fable, GPT 5.6); 256K was common earlier this year.
- Context is not free: prefix-cache reads account for most cost.
[Figure: Timeline of Request 1 through Request N+1, with a compaction step before the last request.]

=== Page 14 ===
Title: Summary: The Agentic Loop. Prompt and context → model proposes → harness executes → result folds into context. The loop repeats until the task is done.
[Figure: Four-step cycle diagram of the loop.]

=== Page 15 ===
Title: Tools and Memory Enable Agentic Capability. Components: LLM (reasoning and planning), Memory, Agent, Tool/Action, Observation, Environment.
[Figure: Diagram linking LLM, memory, agent, tool/action, observation, and environment in a cycle.]

=== Page 16 ===
Title: Agent Memory. Three parts: State (context and memory), LLM (stateless), and Tools (act).
[Figure: Three boxes: State, LLM, Tools, with arrows between them.]

=== Page 17 ===
Title: Context Is One Type of Memory.
- Agents are stateless between runs; each session starts from zero.
- In practice, "memory" is files loaded at session startup.
- Every memory is a decision about what gets re-read in future sessions.
- Context (working memory): what the model sees now; lost when the session ends.
- Persistent memory: survives sessions and reloads next time.

=== Page 18 ===
Title: Why Agents Need Memory. Memory turns repeated instruction into convention. Four problems it solves:
- Repeated instructions: same setup explained every session.
- Lost decisions: the "why" disappears when the window compacts.
- Repeated discovery: agent re-reads files to relearn layout.
- Inconsistent behavior: different sessions make different choices.

=== Page 19 ===
Title: Two Systems Carry Knowledge Forward. Both load at the start of every session.
Table (CLAUDE.md files vs. auto memory):
- Who writes it: You vs. Claude.
- Contents: instructions and rules vs. learnings and patterns.
- Scope: project, user, or org vs. per repository, shared across worktrees.
- Loaded: every session vs. every session (first 200 lines / 25KB).
- Use for: standards, workflows, architecture vs. preferences, corrections, project context.

=== Page 20 ===
Title: Two Systems Carry Knowledge Forward. Duplicate of page 22 with the same table.

=== Page 21 ===
Title: Where CLAUDE.md Lives. Files load broadest scope first; the closest file is read last.
1. Managed policy: …/ClaudeCode/CLAUDE.md. Org-wide, cannot be excluded.
2. User instructions: ~/.claude/CLAUDE.md. Your preferences for every project.
3. Project instructions: ./CLAUDE.md or ./.claude/CLAUDE.md. Team-shared through source control.
4. Local instructions: ./CLAUDE.local.md. Personal, gitignored.
[Figure: Stacked hierarchy of four levels, broadest at top, closest at bottom.]

=== Page 22 ===
Title: What Belongs in CLAUDE.md. "Context is rented, memory is owned."
- Size: under 200 lines per file.
- Structure: Markdown headers and bullets.
- Specificity: concrete rules, not vague ones.
- Consistency: no contradictory or stale rules.
- Belongs: test, build, and lint commands; hard constraints (never commit to main, never edit generated files); facts the agent can't cheaply infer (layout, ownership, gotchas).
- Doesn't belong: what the model already knows about the language; style rules a linter enforces; long prose, changelogs, secrets.

=== Page 23 ===
Title: Getting Too Long? Split It Into .claude/rules/. One topic per file; rules load only when relevant.
- One topic per file keeps each short.
- Add a paths: frontmatter so the rule loads only for matching files (no paths means every session).
- Example tree: .claude/rules/ containing testing.md, api-style.md, db-migrations.md.
- Lessons: scoped rules keep context small; CLAUDE.md stays short and detail lives in rules.

=== Page 24 ===
Title: Auto Memory: Claude's Own Notes. Memory types:
- user: your role, expertise, working preferences.
- feedback: corrections you give and approaches you confirm.
- project: ongoing work and decisions not in the code.
- reference: information living outside the project.
- Location: ~/.claude/projects/<project>/memory/ containing MEMORY.md, user_role.md, feedback_testing.md, and other topic files.
- Behavior: a type field tags every file; MEMORY.md is the index (first 200 lines or 25KB load each session); machine-local, worktrees share the directory; on by default, disable with /memory.
[Figure: Directory tree of memory files under the project memory folder.]

=== Page 25 ===
Title: Retrieval Uses an Index. Index always loads; topic files load only when relevant.
Steps: (1) session starts; (2) load MEMORY.md index; (3) identify relevant topic; (4) read topic file on demand; (5) apply memory to the task.
[Figure: Five-step flow from session start to applying memory, with MEMORY.md as the index.]

=== Page 26 ===
Title: Inspecting and Controlling Memory. Four commands:
- /memory: browse, edit, delete, or disable memory.
- /context: see which instruction files loaded.
- /init: generate a starter CLAUDE.md.
- /doctor: identify content that may not belong in CLAUDE.md.

=== Page 27 ===
Title: The Cost of Remembering. Every permanent token is rent, paid at the start of every session.
- Memory competes with the task for the same window.
- Stale memory is worse than none; it misleads.
- Treat memory like code: review, prune, and keep it in version control.
- Context is limited, and you pay for every token sent to Anthropic.

=== Page 28 ===
Title: Tools and Memory Enable Agentic Capability. Repeat of the page 18 diagram (LLM, memory, agent, tool/action, observation, environment).
[Figure: Same cycle diagram as page 18.]

=== Page 29 ===
Title: Become an Actionable Agent: The Core Tools. Six tools:
- Read: open files and inspect state; the most used tool.
- Search: grep and glob to find things without reading everything.
- Fetch: pull a page or doc; brings untrusted text in.
- Edit/Write: change files; the first tool with consequences.
- Shell: build, test, git; the whole machine unless sandboxed.
- Delegate: spawn a subagent that returns a summary.
- The model decides which tools to use. You will build these yourself in Assignment 2.

=== Page 30 ===
Title: Extending an Agent: Skills, MCP, Hooks and Plugins (section divider).

=== Page 31 ===
Title: Extending an Agent. Four mechanisms solve different problems:
- Skill: how the agent should perform a task.
- MCP: which external data and actions it can reach.
- Hook: what happens automatically at a lifecycle event.
- Plugin: how extensions are packaged and distributed.
- Summary: a skill decides how, MCP reaches outside, a hook enforces, a plugin distributes.
[Figure: Four labeled boxes for skill, MCP, hook, and plugin.]

=== Page 32 ===
Title: Extension Points in the Agent Loop. Each mechanism attaches at a different point:
- User request → model reasoning: skill provides knowledge and procedure.
- Tool selection: MCP provides external tools.
- Tool execution: hook can inspect, block, or react at any stage.
- Plugin packages skills, MCP servers, and hooks into one installable unit.
[Figure: Loop diagram with the four mechanisms attached at their points.]

=== Page 33 ===
Title: Release Workflow Example. Prepare a release, validate, publish to GitHub, notify the team.
- Follow release procedure: skill.
- Create the GitHub release: MCP.
- Prevent publishing when tests fail: hook.
- Share the complete setup: plugin.

=== Page 34 ===
Title: Skills as Reusable Procedures. Knowledge and procedure loaded when the task calls for it.
- Skills carry domain knowledge, reference material, and repeatable workflows.
- Invocation: model-invoked or user-invoked.
- Reasoning happens at run time; think of it as context engineering.
- Example: /release 2.4.0.
[Figure: Skill contents (knowledge, reference, workflows) feeding into a run-time invocation.]

=== Page 35 ===
Title: Skill Structure. A folder, a discovery description, and a body holding the procedure.
- Tree: .claude/skills/release/ containing SKILL.md, references/, scripts/.
- Frontmatter: name: release; description: Prepare a release.
- The description controls discovery; the body holds the procedure; supporting files add references and scripts; users can run it directly with /release.
- Release procedure steps: (1) read release notes; (2) confirm version; (3) run tests; (4) prepare commit; (5) ask before publishing.

=== Page 36 ===
Title: Skill Invocation and Context Cost. Two modes:
- Model-invoked: Claude loads the skill when its description matches the task.
- User-invoked: the user runs /<skill-name>.
- Costs: descriptions load at session start; the full body loads only when the skill runs.
- Side-effecting workflows should usually require explicit invocation.
- Clear, distinct descriptions reduce wrong skill selection.

=== Page 37 ===
Title: MCP as an External Capability Layer. Model Context Protocol connects the agent to external services through a standard protocol.
- Examples: read and update GitHub issues; query a database; retrieve monitoring data; access Figma designs; post to Slack; control a browser.
- MCP provides capabilities that exist neither in the model nor in local files.
[Figure: Grid of example external services (GitHub, database, monitoring, Figma, Slack, browser).]

=== Page 38 ===
Title: How an MCP Tool Call Works. Six steps:
1. Claude identifies a needed action.
2. The MCP client uses a tool.
3. The MCP server handles the connection.
4. The external service performs the operation.
5. Structured results return to Claude.
6. Claude evaluates the result.
- Almost identical to a local tool: same name, description, and typed schema; same call-and-return contract; it runs in another process.
- The protocol carries the call; the agent still decides whether to make it.
[Figure: Six-step sequence from Claude through client, server, and external service, and back.]

=== Page 39 ===
Title: Hooks as Lifecycle Automation. A session runs left to right; hooks fire at marked events.
- Session start: load context, log.
- User prompt: validate or add context.
- Before tool use: inspect or block.
- After tool use: format, test, log.
- Before stopping: verify tests.
- Model reasoning is not an event, so no hook.
- Hooks can run commands, HTTP requests, MCP tools, prompts, or subagents.
[Figure: Timeline: session start, user prompt, model reasoning, tool call, tool result, stop, with hook points marked.]

=== Page 40 ===
Title: Plugins as the Packaging Layer. One installable unit containing skills, hooks, agents, and MCP config.
- Tree: plugin/ with skills/, hooks/, agents/, .mcp.json, .lsp.json, .claude-plugin/plugin.json.
- Benefits: one-command installation, pinned-release versioning, namespacing (no name clashes), team reuse, marketplace distribution.
- A plugin is how a working setup becomes something others can install.
[Figure: Directory tree of a plugin package.]

=== Page 41 ===
Title: How the Four Mechanisms Fit Together. Judgment, capability, enforcement, and packaging.
- Skill: knowledge and procedure.
- Claude: reasoning and tool use.
- MCP: GitHub, Slack, databases.
- Hook: fires at lifecycle events, before and after every tool call.
- Plugin: packages the skill, MCP config, and hooks for installation elsewhere.
[Figure: Diagram with Claude at center, linked to skill, MCP, and hook, enclosed by a plugin boundary.]

=== Page 42 ===
Title: Inside .claude/. Directory contents: CLAUDE.md, settings.json, settings.local.json, commands/, skills/, agents/, hooks/, plugins/.
- Memory: CLAUDE.md and rules/.
- Configuration: permissions, hooks, env.
- Workflows: skills/ and commands/.
- Delegation and guardrails: agents/ and hooks/.
- Same layout exists at ~/.claude/ for user scope. Project settings override user settings.
[Figure: Tree of the .claude/ directory with grouped purposes.]

=== Page 43 ===
Title: Design Exercise. Classify each requirement and explain why the others don't fit. Hands up = score.
- Apply company API conventions: Skill.
- Read an issue from Jira: MCP.
- Run formatting after every edit: Hook.
- Guide a multi-step deployment: Skill.
- Send a completion notification: Hook plus MCP.
- Block writes to production: Hook or policy.
- Share everything across repositories: Plugin.
- Summary: skill = knowledge and procedure; MCP = external access; hook = event automation; plugin = packaging and distribution.

=== Page 44 ===
Title: Next class. Agent from a user's perspective II.

=== Page 45 ===
Title: Optional slides (section divider).

=== Page 46 ===
Title: MCP: What and Why. Purpose: access to external tools and services.
- Before MCP: N×M custom integrations between clients and services.
- MCP avoids a unique integration for every AI client.
- Defined as an open, stateless protocol letting an AI application discover and use capabilities that external servers expose.
- Reference: modelcontextprotocol.io.
- Question posed: how to reach external services such as Gmail or GitHub.
[Figure: N×M grid of clients and services replaced by a single protocol layer.]

=== Page 47 ===
Title: MCP Architecture. Four parts:
- Host: Claude Code, the app you talk to.
- MCP client: one connection per server, run by the host.
- MCP server: exposes a system's capabilities as tools.
- External system: GitHub, Slack, PostgreSQL, or a local service.
- Connections use the MCP protocol.
[Figure: Host containing a client, linked by the MCP protocol to a server, which connects to an external system.]

=== Page 48 ===
Title: MCP: Three Core Primitives.
- Tools: actions Claude can call, e.g., create_issue(…).
- Resources: readable data, e.g., github://issues/123 (an issue or schema).
- Prompts: reusable templates a server exposes, e.g., triage_issue(…). The prompt returns instructions: review issue #123, determine reproducibility, assess severity as high, recommend an owner and next action.
- Prompts are user-controlled; in Claude Code they appear as namespaced slash commands, e.g., /mcp__github__triage_issue 123 high.

=== Page 49 ===
Title: How They Work Together. Example request: "Triage issue #123 and assign it if it is a critical authentication bug."
- Prompt triage_issue: supplies the organization's triage procedure.
- Resource github://issues/123: supplies the issue content.
- Tool get_related_errors: retrieves current diagnostic information.
[Figure: Three primitives (prompt, resource, tool) feeding into one task.]

=== Page 50 ===
Title: MCP Security: The Essential Part. A connected server can see what you send and act with your credentials.
- Least privilege: scope tokens to the repo, table, or channel needed.
- Read vs. write: separate reads from writes; keep mutations behind approval.
- Distrust tool output: never treat returned content as instructions.
- Vet before installing: third-party servers can carry prompt injection.
- Ask before connecting: what can it read, and what can it change?

=== Page 51 ===
Title: What an MCP Gateway Is. A control layer between an AI client and one or more MCP servers.
- Like an API gateway, but speaks MCP (tools/list, tools/call, resources, prompts, schemas, protocol versions).
- An architectural pattern; to the client it looks like another MCP server.
- Diagram: Claude Code or agent → MCP gateway (auth, policy, logging, routing, rate limits) → GitHub MCP, Jira MCP, Database MCP.
[Figure: Client connected to a gateway, which fans out to GitHub, Jira, and database MCP servers.]

=== Page 52 ===
Title: What a Gateway Does. Labeled OPTIONAL.
1. Aggregate: one connection and one namespaced catalog (github.*, jira.*, postgres.*).
2. Route: forwards calls to the owning server; Mcp-Method headers route without reading the body.
3. Enforce policy: controls who connects, which tools are visible, callable, or need human approval.
4. Broker identity: client authenticates once; upstream credentials stay behind the gateway.
5. Observe: central audit trail (identity, tool, decision, latency, outcome, cost).
6. Scale: load balancing, retries, circuit breakers, catalog caching, quotas.
- Worth it when many users, agents, servers, credentials, or compliance rules must be governed consistently.
- Risks: it is a trust boundary; broad credentials, lost end-user identity, name collisions, secrets in logs, single point of failure.

=== Page 53 ===
Title: What is new? Labeled OPTIONAL. Spec 2026-07-28 is the largest MCP revision since launch.
- Stateless core: no sessions to hold; any request can reach any instance behind a plain load balancer.
- Routing: Mcp-Method headers let gateways route without reading the body; list results are cacheable with a TTL.
- Extensions: Tasks (long-running work) and MCP Apps (server-rendered UIs) now ship as extensions.

TOTAL PAGES: 53
