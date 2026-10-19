# L08 slides 逐頁筆記

- 來源：https://cs2680.com/slides/8_agent_design_5.pdf
- 頁數：54（PDF 檢視器的頁數，封面 = 1）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。

註：slide 右下角印的 footer 頁碼與 PDF 頁數不同（footer 從 2 起算且跳號：PDF 1–26 = footer 2–27；PDF 27 = footer 30；PDF 28–35 = footer 31–38；PDF 36–44 = footer 40–48；PDF 45 = footer 51；PDF 46 = footer 53；PDF 47–53 = footer 54–60；PDF 54 無 footer）。本檔一律用 PDF 頁數。

=== Page 1 ===
Cover. Title: "Modern AI systems: agents and system optimizations." Presenter: Juncheng Yang. Lecture: "Agent design V: cost-effective agents." Affiliation/site: Harvard MaDSys · course.agentic-system.org.

=== Page 2 ===
Logistics (assignments).
- Assignment 3 starts today. It is much harder than earlier assignments.
- Leaderboard: limited submissions per day; no late days.
- Assignment 3 is worth 20% of the grade. Treat it like a midterm. Start early.
- Office hours next week (time TBA).
- Assignment update: Assignment 4 is now worth 20 points; Assignment 5 is worth 10 points.
- Reason: Assignment 5 was too hard and overlapped with the course project and other courses' projects.

=== Page 3 ===
Logistics (schedule and session logs).
- Schedule update: some lectures move earlier to fit the assignment changes.
- Two bonus paper-presentation lectures; sign-up opens today.
- Claude Code session log: update the logs for all related sessions.
- "Do NOT alter session logs" — doing so violates academic integrity.

=== Page 4 ===
Plan for today.
1. Cost-effective agents
2. Agent architecture
3. Coding agent case study

=== Page 5 ===
Section opener: "Design Cost-Effective Agents."
- Scope note: this lecture focuses on LLM cost and ignores other compute costs.

=== Page 6 ===
Recall the structure of a session.
- A session contains multiple turns (Turn 1, Turn 2, Turn 3, ...).
- Within one turn the flow is: User message → Model call → Tool call → Model call → Reply to user.
- One user turn = multiple LLM steps and tool steps.
- [Figure: Session diagram; a session split into turns, one turn expanded into user message, model call, tool call, model call, reply.]

=== Page 7 ===
Where does cost come from?
- Cost = Users × Sessions/User × Turns/Session × Steps/Turn × Tokens/Step × Price/Token.
- Users × Sessions/User: GROW with adoption and engagement.
- Turns/Session, Steps/Turn, Tokens/Step: SHRINK with better agent trajectories.
- Price/Token: SHRINKS with unit price.
- [Figure: The multiplicative formula with the factors grouped in three colors, annotated "grow" (adoption/engagement) and "shrink" (trajectories, unit price).]

=== Page 8 ===
Your Claude Code usage: turns per session.
- Most sessions contain only one prompt. Positive: most students start a new session per task.
- A few students run marathon sessions, defined as 100+ turns.
- Single-prompt sessions: 68% (Assignment 1), 75% (Assignment 2).
- [Figure: Bar chart of single-prompt session share, 68% (A1) vs 75% (A2).]

=== Page 9 ===
Reduce (user) turns per task.
- Turn k re-reads turns 1 through k−1, so total cost grows with the square of the turn count.
- Users come back when: there is no plan; the agent stopped early; the output was never checked.
- Techniques:
  - Front-load planning: confirm the goal and plan once, before acting.
  - Structured task decomposition: split into subtasks, each with a "done" check.
  - Self-verification before handoff: run tests and check output before returning.
- Goal: finish the task autonomously, with no user check-ins.
- Lever strip (repeated on later slides): turns per task · steps per turn · tokens per step · price per token.
- [Figure: Diagram of turn-to-turn re-reading; each new turn re-reads all prior turns.]

=== Page 10 ===
Your Claude Code usage: steps per turn.
- Most turns take few steps, mostly because effort is set to medium or high.
- Some turns run almost 1,000 steps.
- Median steps per turn: 3 (Assignment 1), 4 (Assignment 2).
- [Figure: Bar chart of median steps per turn, 3 (A1) vs 4 (A2).]

=== Page 11 ===
Reduce steps per turn.
- One call per action: 4 model calls, each followed by a tool call (Model → Tool → Model → Tool → ...).
- Plan, then batch: 2 model calls, with 3 tools run in parallel between them.
- Batch independent calls: read five files in one step instead of five steps.
- Reuse plans and skills: replay what worked before instead of re-deriving it.
- Load context up front: read the files you need at the start, not one per step.
- Every model call re-reads the full context, so fewer calls cost less.
- [Figure: Two timelines; 4 sequential model/tool pairs vs 2 model calls with 3 parallel tools between.]

=== Page 12 ===
Reuse plans, skills and experience: related papers (ADVANCED, skim or read on your own).
- Skill libraries: Voyager (2023) stores executable skills; SkillRL (2026) improves the skill library and the agent policy jointly.
- Insights from experience: ExpeL (2023) extracts reusable insights; ReasoningBank (2025) keeps strategies from both successful and failed runs.
- Playbooks and plan templates: Test-Time Plan Caching (2025) reuses and adapts plan templates.
- Durable conversational memory: Mem0 (2025) stores and updates facts; LightMem (2025) consolidates offline; SimpleMem (2026) compresses memory.
- Takeaway: reuse pays when tasks recur; memory upkeep and stale entries can erase the savings.

=== Page 13 ===
Your Claude Code usage: tokens per step.
- Main agent: median 200K–300K tokens per step; p90 600K–700K.
- Subagent: median ~80K tokens per step; p90 ~200K.
- Main-agent median: 208K (Assignment 1) vs 301K (Assignment 2).
- [Figure: Bar chart of main-agent median tokens per step, 208K (A1) vs 301K (A2).]

=== Page 14 ===
Your Claude Code usage: tokens over steps.
- Context accumulates and grows quickly as steps increase.
- Context at step ~500: 670K (Assignment 1), 650K (Assignment 2).
- [Figure: Line/bar chart of context size vs step count, rising steeply; ~670K (A1) and ~650K (A2) at step ~500.]

=== Page 15 ===
Your Claude Code usage: most tokens are cache read.
- Cache-read token share: 97.6% (Assignment 1).
- Output is ~5× smaller than fresh prefill (cache write).
- Fresh prefill is ~100× smaller than cache reads.
- Typical price ratio, cache read : input : output = 1 : 10 : 50.
- [Figure: Token-volume and price-ratio comparison of cache read, fresh input, and output.]

=== Page 16 ===
Reduce input tokens per step: keep context lean.
- Principle: tokens that stay in context are paid for again on every later step.
- Drop what's stale: truncate stale results; mask tool outputs already used; compact the history (summarize old turns into state).
- Shrink what enters: compress observations (keep errors, not the full log); offload to files (save big outputs and pass a path).
- Load only what's needed: retrieve selectively (only relevant tools and memory); isolate exploration (a sub-agent returns a summary).
- [Figure: Three-column diagram — "Drop what's stale", "Shrink what enters", "Load only what's needed".]

=== Page 17 ===
Reduce input tokens per step: related papers (ADVANCED, skim or read on your own).
- Compress agent history: ACON (2025) cut peak context 26–54%; Active Context Compression (2026) — agent compacts itself, 23% fewer tokens; TRACE (2026) — summaries cause rework.
- Context as external memory: MemGPT (2023) treats context as fast memory; Scroll (2026) keeps a lossless external log, code picks what the model sees.
- Prompt compression: LLMLingua (2023) up to 20× fewer tokens; LongLLMLingua and LLMLingua-2 (2024); Prompt Compression in the Wild (2026) pays off only on long prompts.
- Keep tool data out of context: Code execution with MCP (2025) filters results in code, 150K → 2K tokens; Tool Search (2025) 85% fewer tool tokens; Programmatic Tool Calling 37% fewer tokens.

=== Page 18 ===
Reduce output tokens per step: ask for less.
- Prompt-level constraints: state length, format, and what to skip.
  - Example instructions: "Answer in ≤100 words." / "Return only JSON." / "One sentence. Top 3 items." / "Don't restate the problem." / "Don't explain your reasoning."
  - Terse system prompt example: "Be concise; omit background unless requested."
- Output-token caps: set a hard limit in the API call, e.g. max_tokens=300 or max_output_tokens=300.
  - Simple, but truncation can cut an answer mid-sentence.
  - Pair the cap with a concise-output prompt.
  - Catch: reasoning can use up the cap.

=== Page 19 ===
Reduce output tokens per step: schema and effort.
- Structured output: require a schema with only the needed fields. Example: {"action": "search", "argument": "KV cache"}.
  - Restrict enums and optional fields so the model cannot add extras.
  - Suits tool-using agents: prose around a tool call is pure cost.
- Adaptive reasoning effort: match the thinking budget to the step. Example: lookup uses effort="low"; debug uses effort="high".
  - Low effort for lookups and formatting; high for planning and debugging.
  - Set per call or per step, as a reasoning-effort level or a thinking-token budget.
- [Figure: Code-style JSON tool-call object with "action" and "argument" fields.]

=== Page 20 ===
Reduce output tokens per step: related papers (ADVANCED, skim or read on your own).
- Prompts and budgets: Concise CoT (2024) asks for brevity; CCoT (2024) word limits on chain-of-thought; Chain of Draft (2025) terse drafts; TALE (2024) reasoning-token budget.
- Adaptive reasoning effort: Ares (2026) picks effort per step; When to Plan (2025) plans only when useful; s1 and L1 (2025) enforce thinking budgets; Reason Efficiently; ShorterBetter.
- Structured output and decoding: Let Me Speak Freely? (2024) finds strict formats can hurt reasoning; XGrammar and SGLang (2024); JSONSchemaBench (2025).
- Emit only what changes: AdaEdit (2026) chooses diff vs whole file; CodeStruct (2026) AST-level edits; Tool-making agents (2026) — reusable tools cut output tokens 58%.

=== Page 21 ===
Reduce price per token: caching and batching.
- Chart of price relative to base input token (Claude API): batch + cached input 0.05×; cached input 0.1×; batch input 0.5×; base input token 1×; output token 5×.
- Maintain stable prefixes: keep system prompt, tools, and early history unchanged so they are cacheable.
- Batch what can wait: evals, backfills, bulk jobs.
- [Figure: Horizontal price-ratio chart with ticks 0.05×, 0.1×, 0.5×, 1×, 5×, ordering the five token types from cheapest to most expensive.]

=== Page 22 ===
Reduce price per token: model routing.
- Choose up front: pick one model per turn before generating. A router can be trained on preference data and can also pick agent roles.
- Escalate on failure: try a cheap model first; move up when a check fails. Checks: a learned scorer, self-verification, or execution feedback.
- Re-route each step: reselect models as the trajectory grows, routing on history and budget. An orchestrator can call models as tools.
- Hard part: one cheap planning mistake can waste many later actions.

=== Page 23 ===
Reduce price per token: system techniques in later lectures.
- Model optimization: MoE/sparsity, quantization, pruning, distillation, workload-targeted fine-tuning.
- Serving engine optimization: speculative decoding, KV-cache optimization, better request scheduling.
- Hardware: faster kernels, better kernel scheduling, specialized accelerators.
- Lever strip at bottom: turns per task · steps per turn · tokens per step · price per token.

=== Page 24 ===
Reduce price per token: related papers (ADVANCED).
- Prefix caching: vLLM (2023) PagedAttention; SGLang (2024) RadixAttention prefix cache; Prompt Cache (2024) modular reuse.
- Choose up front: RouteLLM (2024) learned router; MasRouter (2025) also picks agent roles.
- Escalate on failure: FrugalGPT (2023) learned cascade; AutoMix (2023) self-verification; EcoAssistant (2023) execution feedback.
- Re-route each step: ToolOrchestra (2025) small orchestrator; BAAR and MTRouter (2026) budget-aware routing.

=== Page 25 ===
Every saving has a counter-cost.
- Compaction vs. reconstruction: dropped files get re-read, and the summary rewrites the cache.
- Routing vs. longer failures: one bad plan from a cheap model can add many steps or a failed attempt.
- Subagents vs. duplicated context: each subagent re-reads shared files and instructions.
- Speculation vs. wasted work: wrong guesses burn tokens and contend for the same tools.
- Net saving = gross saving − counter-cost. Measure both on the same tasks.

=== Page 26 ===
Cap each task's budget and stop when progress stalls.
- Per-task limits (illustrative example values): dollars $10; model calls 80; tool time 15 min; retries per step 2.
- Set limits from traced runs, e.g. 2× the p95 of successful tasks.
- Stop when: the verifier passes; no new passing test in N steps; the same error repeats; a limit is hit (hand off with a summary).
- A task that stops with a summary costs less than a runaway one.

=== Page 27 ===
Do you need an LLM at all?
- Four question → approach rows:
  - "Same steps every time?" → Write a script. "Have the LLM write the code once, then just run it."
  - "Fixed input format?" → Parse with rules. "Regex, parsers and templates cost nothing per call."
  - "Narrow label or score?" → Train a small classifier. (Example text garbled in extraction, printed roughly as "GBM or Jev!" — likely gradient-boosted model or a small classifier; check the original slide.)
  - "Fixed workflow, little reasoning?" → Script the workflow. "Call the LLM only at the steps that need it."
- Bottom line: "Reach for an LLM only when a step needs reasoning."
- [Figure: Decision layout, four question boxes each leading to an approach box with a one-line rationale, ending at the bottom-line box.]

=== Page 28 ===
Section opener: "Make Your Agent Faster."
- Subtitle: faster agents are usually, but not always, cheaper too.
- Topics: speed up LLM serving; improve orchestration; speed up tool calls; parallelize work; speculative actions.

=== Page 29 ===
Completion time is the critical path, not the sum of every step.
- Serial: time ≈ sum of all steps (Queue, Setup, Prefill, Reasoning, Tools, Orchestration).
- Parallel: time ≈ critical path (Plan → Worker A ‖ Worker B → Merge). Red marks the critical path.
- Cheaper can be slower: small models may take more steps.
- Parallel work costs more: less waiting, but more total tokens.
- [Figure: Serial timeline of stacked stages vs. a parallel plan/worker/merge graph with the critical path highlighted in red.]

=== Page 30 ===
Speed up LLM serving.
- Every cost technique from the previous section also cuts latency: fewer turns, fewer steps, fewer tokens, cheaper serving (e.g. caching, smaller models).

=== Page 31 ===
Improve orchestration.
- Async execution: start the next step while a tool call runs.
- Persistent sessions: keep one shell or browser open across steps.
- Stream and pipeline: start the tool call before the LLM response finishes.
- Colocate services: run tools on the same host as the model.

=== Page 32 ===
Speed up tool calls.
- Builds, tests, and page loads can take longer than the model call itself.
- Cache tool results: repeated reads and searches hit the cache.
- Faster hardware: run heavy compute on a server, not a laptop.
- Better tools: faster, cheaper tools for the same job; call tools selectively.
- Fail fast: time out hung calls.
- Measure tool time per step before tuning the model.

=== Page 33 ===
Parallelize work.
- Sequential: read file A, then B, then C. Parallel: read A, B, C together — same work, a third of the wait.
- Parallel tool calls: issue independent calls in one step.
- Parallel sub-agents: split independent subtasks and merge their summaries.
- Only independent work can run in parallel; shared state needs a merge step.
- [Figure: Sequential vs. parallel timelines for reading files A, B, C.]

=== Page 34 ===
Speculative actions.
1. Predict: a cheap model guesses the next action.
2. Run early: execute the guess while the main model is still thinking.
3. Compare: check the guess against the main model's choice.
- Guess matches: the result is ready; the wait is skipped.
- Guess misses: discard it; the cost is one wasted call.
- Pays off when guesses are often right and actions can be undone.
- Open question: how to schedule speculative calls under limited GPU, CPU, and API budgets so the critical-path time saved exceeds the work wasted.

=== Page 35 ===
What gets speculated (ADVANCED). Table; the speculation horizon grows from a single call to a whole trajectory.
- Tool intent — which tool comes next — SPORK [8]
- Tool call — the tool plus its arguments — PASTE [5]; Speculative Tool Calls [2]
- Next action — any action or API response — Speculative Actions [1]
- Branches — several possible paths at once — B-PASTE [6]
- Trajectory — a multi-step chain, already executed — Speculative Macro Commit [10]
- Sources: [1] Speculative Actions (ICLR 2026); [2] Speculative Tool Calls (arXiv 2025); [5] PASTE (arXiv 2026); [6] B-PASTE (arXiv 2026); [8] SPORK (arXiv 2026); [10] Speculative Macro Commit (arXiv 2026).

=== Page 36 ===
Where predictions come from (ADVANCED).
- Model-based: a small draft model predicts what the large model will do next — Speculative Actions [1], Speculative Tool Calls [2].
- Self-speculative: an early fork of the same model predicts its own later tool call — SPORK [8].
- History-based: past traces predict the next tool, with arguments bound to the last result — PASTE [5], Speculate with Memory [9].
- Lossless methods always verify before keeping speculated work. Lossy: SPAgent [3] skips some checks.
- Sources: [1] Speculative Actions (ICLR 2026); [2] Speculative Tool Calls (arXiv 2025); [3] SPAgent (arXiv 2025); [5] PASTE (arXiv 2026); [8] SPORK (arXiv 2026); [9] Speculate with Memory (arXiv 2026).

=== Page 37 ===
Two examples.
- PASTE [5] — predict the next tool from past traces. Pattern: search(q) → visit(results[0].url) → extract(page). Once search(q) starts, the trace pattern says a visit comes next; the URL is filled from the search result, so visit runs while the model is still generating.
- SPORK [8] — the model predicts its own tool call. A "think:" reasoning block of about 2,000 tokens; an early probe issues search(q); later the main model emits tool_call search(q) and the result is already ready. Tool intent is often clear early in reasoning, so a forked probe launches the call ahead of time.
- [Figure: Two text-based flow diagrams — PASTE's tool chain and SPORK's think → probe → tool_call timeline.]

=== Page 38 ===
Optimize in a loop: run, measure, change, again.
1. Run and profile: log every call, token, tool, and wait.
2. Measure: understand the source of cost and latency.
3. Change one thing: compaction, routing, caching, or parallelism.
4. Re-evaluate on the same tasks: success, spend, p95 latency. Then repeat.
- Callout: "Remember this for your Assignment 4!"
- [Figure: Four-step cycle diagram with a repeat arrow.]

=== Page 39 ===
Section opener: "Agent Architecture." Subtitle: Monolithic · Modular · Microkernel.

=== Page 40 ===
Three harness architectures.
1. Monolithic harness: everything lives in one runtime; the agent contains memory, tools, context, planning, and execution.
2. Modular harness: interfaces with one controller; providers are MemoryProvider, ToolProvider, ContextProvider, SandboxProvider.
3. Agent microkernel: the core keeps only coordination (state, scheduling, security) and reaches memory, tools, and execution services through standardized protocols.
- Shift: responsibility moves out of the agent — from code, to interfaces, to services.
- [Figure: Three block diagrams — agent with internal components; agent with pluggable providers; runtime connected to external services.]

=== Page 41 ===
Monolithic harness: one runtime implements memory, tools, context, planning and execution.
- Code sketch: class CodingAgent creates Memory, Tools, ContextManager, Planner, Executor; run(task) loops until done — plan, execute, update context.
- Advantages: simple to implement and debug; minimal communication overhead; internal state easy to share; low execution overhead.
- Disadvantages: hard to replace one component; components tightly coupled; hard to share infrastructure across agents; isolation hard to enforce.
- Key characteristic: the agent owns everything, in one runtime.

=== Page 42 ===
Modular harness: the agent still controls the loop but reaches each component through an interface.
- Code sketch: CodingAgent(memory_provider=RedisMemory(), tool_provider=MCPTools(), context_provider=SlidingWindowContext(), sandbox_provider=DockerSandbox()). Comment: swapping Docker for Firecracker means changing one provider.
- Comparison: monolithic has built-in memory; modular has a MemoryProvider (e.g. RedisMemory).
- Advantages: easy component replacement; better testing and extensibility; clear separation of responsibilities; third-party implementations can plug in.
- Disadvantages: the controller still owns the lifecycle; coordination logic grows complex; failure domains can still be shared; joint tuning requires controller edits.
- Key characteristic: one controller delegates through interfaces.
- [Figure: Side-by-side diagram, built-in memory vs. MemoryProvider.]

=== Page 43 ===
Agent microkernel: a small runtime coordinates, and external services provide the capabilities.
- Agent runtime (state, coordination, scheduling, security) connects over a standardized protocol to three services: Memory service (database), Tools service (tool APIs), Execution service (sandboxes).
- Services can run in separate containers or on separate machines.
- Advantages: services scale independently; better fault isolation; stronger isolation if enforced; shared, centrally managed infrastructure.
- Disadvantages: higher communication overhead; more failure modes; harder end-to-end debugging; needs standard protocols and lifecycles.
- Key characteristic: the runtime coordinates; external services provide capabilities.
- [Figure: Central runtime box connected to three service boxes.]

=== Page 44 ===
Running one Python snippet: only the microkernel hands sandbox management to its own service.
1. Monolithic: agent executes Python locally — fewest hops; isolation hard to enforce.
2. Modular: agent calls SandboxProvider.run(code), which executes the Python — swap the provider, not the agent.
3. Microkernel: agent runtime sends an execution request → execution service allocates a sandbox → sandbox executes Python and returns the result. The execution service owns allocation, isolation, and sandbox lifecycle.
- [Figure: Three sequence diagrams of one Python execution across the three architectures.]

=== Page 45 ===
The microkernel trades simplicity and low overhead for isolation, sharing and scale. Comparison table (Monolithic / Modular / Microkernel):
- Design principle: Everything integrated / Interface abstraction / Minimal core + services
- Central controller: Yes / Yes / Yes, but reduced
- Component replacement: Difficult / Easy / Easy, if protocols match
- Execution isolation: Optional / Optional / Architectural emphasis
- Component deployment: Usually together / Together or separate / Often independent
- Independent scaling: Limited / Possible / Strong
- Communication cost: Low / Low–medium / Potentially higher
- Typical use case: Standalone agents / Agent frameworks / Multi-agent infrastructure
- Takeaway: monolith for standalone agents, microkernel for multi-agent infrastructure.

=== Page 46 ===
The eight harnesses (abbrev · name · maker · language · one-line idea).
- CC · Claude Code · Anthropic · TypeScript (closed) · Policy layer and typed hooks around Claude.
- CX · Codex CLI · OpenAI · Rust · Sandbox first, ask second.
- DSH · DeepSeek Harness · DeepSeek AI · TypeScript · Everything is a plugin, even the loop.
- OC · OpenCode · Anomaly (SST) · TypeScript/Bun · A session server with thin clients.
- PI · Pi · Mario Zechner / Earendil · TypeScript · A small core you extend in TypeScript.
- OMP · oh-my-pi · Can Bölük / Stencil Labs · TypeScript + Rust · Pi fork with native tools and the IDE wired in.
- CLAW · OpenClaw · OpenClaw Foundation · TypeScript · An assistant gateway for chat channels.
- HM · Hermes Agent · Nous Research · Python · An agent that writes its own skills.
- Note: the deck has "Unique to ..." slides for seven of the eight (no separate slide for Claude Code).

=== Page 47 ===
Unique to Codex CLI.
- Sandbox before approval: commands run in a sandbox with no network access; the agent asks for approval only to go outside the sandbox.
- Patches that obey a grammar: a Lark grammar defines the patch envelope; the agent matches hunks in four passes.

=== Page 48 ===
Unique to DeepSeek Harness.
- The loop is also a plugin: the loop, adapters, tools, log, and approvals are all plugins; YAML layers can replace any one of them.
- Requests from the log: each model request is a frozen view of the session log; the harness only appends entries.
- Compare-and-swap edits: an edit fails if the file changed after the model last read it.

=== Page 49 ===
Unique to OpenCode.
- The harness is a server: the TUI, the SDKs, and the web app all use the same OpenAPI HTTP server.
- Fuzzy edits with a size limit: nine replacers try matches, from exact to anchor match; the harness rejects fuzzy matches that are too large.
- A snapshot at each step: a shadow git repository lets /undo restore the files, not just the chat history.

=== Page 50 ===
Unique to Pi.
- A minimal core: four tools; no MCP, sub-agents, or approvals; extensions supply everything else.
- Cache warming with a price check: keep-alive requests are sent only when the expected saving is $0.05 or more.
- Libraries for other projects: pi-ai supports 42 providers across 10 wire APIs; three other projects use Pi's code.

=== Page 51 ===
Unique to oh-my-pi.
- Hashline edits: each edit carries a 4-hex file tag and line numbers, so the model does not retype the old text.
- The IDE in the process: one shell stays open across all calls; native tools provide search, AST, LSP, and a debugger.
- Special context methods: snapcompact converts old history into images; TTSR stops generation and retries when a regex matches.

=== Page 52 ===
Unique to OpenClaw.
- A chat gateway with queue lanes: 27 chat channels send messages to one lane per session; a queue mode controls messages that arrive during a run.
- Memory before compaction: a silent turn first writes dated notes; recall combines full-text search and vector search.
- Fences, taint, and sentinels: fences isolate untrusted text; a network read taints the turn; the agent monitors secret sentinels.

=== Page 53 ===
Unique to Hermes Agent.
- A fork that learns: a background fork reviews each nudged turn, then edits the memory and the skills.
- Earliest compaction: compaction starts at 50% of the context window — the earliest of the eight harnesses.
- Save before execution: tool-call rows are written to the session database before any side effect occurs.

=== Page 54 ===
Next class.
- Agent safety and security.
- Self-evolving harness.
