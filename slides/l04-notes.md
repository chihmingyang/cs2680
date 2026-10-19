# L04 slides 逐頁筆記

- 來源：https://cs2680.com/slides/4_agent_design_1.pdf
- 頁數：56（PDF 檢視器的頁數，封面 = 1；與 docs/l04.html 的 data-pages-total 一致）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。
- 頁碼校正：WebFetch 把 slide 右下角的 footer 號碼當頁碼，footer 會跳號（隱藏的 slide）。本檔已換算成 PDF 頁數。 跳過的 footer 號碼：[40]。
  footer → PDF：41–57 → 40–56

=== Page 1 ===
Cover: "Modern AI Systems: Agents and System Optimizations." Juncheng Yang. Agent Design I: context management and tool design. Harvard MadSys, course.agentic-system.org.

=== Page 2 ===
Logistics:
- Assignment 1 is due this Sunday.
- Share your repo and fill in the Google form.
- Assignment 1 sharing sign-up opens this Thursday.

=== Page 3 ===
Plan for today: agent loop (ReAct), tool designs, context management, prompt engineering, context engineering.

=== Page 4 ===
The ReAct loop (Reason and Act in one loop):
- Thought: what do I know, what is missing, what next?
- Action: emit a structured call the environment can run.
- Observation: the environment answers with facts.
- Reason-only fails because nothing checks the reasoning, so small errors compound into confident hallucination.
- Act-only fails because tool calls have no plan behind them and the model repeats itself.
- ReAct works because thoughts steer actions and observations correct thoughts.
- Repeat until observations answer the question or a stopping rule ends the run.
- Source: arXiv 2210.03629.

[Figure: Three-stage cycle of Thought, Action, and Observation, with the ReAct loop shown against reason-only and act-only variants.]

=== Page 5 ===
The agent loop (pseudocode):
- Start messages with a system prompt ("Solve the task using the tools") and the user request.
- For each step up to MAX_STEPS: call the model with messages and tools, append its message, and return if it gives a final answer.
- Otherwise, for each tool call: validate arguments, execute the tool, and append a "tool" message with the serialized result.
- If the step limit is reached, raise "Agent exceeded its step limit."

[Figure: Flowchart of user request → model → next action? → execute tool → return tool result → back to model, with an exit to "return answer" on a final answer.]

=== Page 6 ===
The agent loop, harness view. Harness designer responsibilities are annotated on the loop:
- Assemble the context.
- Validate the request, check permissions, and run the tool.
- Optionally process the result and manage context.
- Write tool definitions.

[Figure: The same loop flowchart with annotations for the harness designer's tasks.]

=== Page 7 ===
Components of a coding agent: three components share one context window and should be designed together.
- 01 Model + agent loop: the LLM proposes an action, sees the result, and repeats. An agent is a model plus a loop.
- 02 Tools and guardrails: search, read, edit, run tests, and shell, all behind permissions, sandboxing, and approval. Tools set capability; guardrails keep it safe.
- 03 State (context and memory): what is in the window now, plus what carries forward between steps. Assemble it and keep what outlives the turn.

=== Page 8 ===
What tools should we provide to agents? Categories: search/read, edit/write, execution, others. Audience poll ("hands up = score").

=== Page 9 ===
How should an agent find relevant code? Audience poll.

=== Page 10 ===
Tool search and read: glob and grep.
- The agent loops over ls, glob, and grep. Nothing to build or keep in sync, and it always reflects the live repo.
- Cost: burns turns and context. Lexical matching misses paraphrases.
- Example, "fix the login timeout":
  1. grep -rn "timeout" src/ gives 37 hits in 12 files.
  2. glob src/**/auth/*.ts narrows to auth/retry.ts.
  3. Read auth/retry.ts, change RETRY_MS = 500, and patch.

=== Page 11 ===
Tool search and read: semantic search.
- Semantic search embeds code chunks and retrieves by meaning.
- Structural search uses a file tree plus ranked symbols (Aider's repo map).
- Fast at query time. The cost is building and re-syncing the index.
- Example: "where do we rate-limit?" returns throttle.ts on the first query.
- Repo map example lists aider/coders/base_coder.py (class Coder, def apply_updates) and aider/commands.py (class Commands) as a ranked outline.

[Figure: Embedding search diagram (query → nearest chunks; same meaning, different words, vectors land close) and a structural repo-map outline of files, classes, and signatures.]

=== Page 12 ===
Tool search and read: extrinsic signals.
- Evidence outside the source: stack traces, failing tests, git history.
- Highest-precision signal when debugging, but only helps when such a signal exists.
- Example, crash report on checkout: read stack trace at cart.ts:88 (3 frames), read tax.ts:20-60 (rounding in applyTax), patch, and run pytest tests/tax.py, which goes green without any search.

=== Page 13 ===
Tool search and read: language server (LSP).
- Queries the compiler's index for definitions, references, symbols, and types.
- Resolves imports, overloads, and renames that grep can only guess at.
- Cost: a live server per language and a slow cold start.
- Example, rename charge() to capture():
  1. textDocument/references finds 42 call sites in 7 files.
  2. textDocument/rename covers aliased imports.
  3. Type check finds no unresolved symbols.

=== Page 14 ===
Search and read comparison (table; columns: approach, finds code by, best when, main cost):
- glob/grep: literal names and paths; name is known or guessable; cost is turns and context per search.
- Semantic index: meaning of embedded chunks; wording won't match the code; cost is building and re-syncing the index.
- Extrinsic signals: traces, failing tests, git history; a report already points at code; only exists for some tasks.
- Language server: compiler's symbol graph; edits must follow references; cost is a live server per language.
- Takeaway: start with grep; reach for an index or LSP when names run out.

=== Page 15 ===
Same search and read comparison table as page 14 (duplicate slide in the deck).

=== Page 16 ===
How should an agent edit code? Audience poll.

=== Page 17 ===
Tool edit: whole-file rewrite.
- The model regenerates the whole file and the tool overwrites it.
- No patch syntax to get wrong, so every edit applies cleanly.
- Cost: output scales with file size, and untouched code can drift.
- Example, add a retry to the API client: read client.ts (120 lines), write the full file with 4 lines changed, and check the diff, which applies on the first try.

=== Page 18 ===
Tool edit: unified diff / patch.
- The model emits a patch and a separate tool applies it.
- Compact and reviewable, the format humans and CI already use.
- Cost: hunks fail when line numbers or context drift.
- Example, bump the retry limit in two files: read client.ts and api.ts, emit a patch with two hunks (@@ -41,3 +41,3 @@, 6 lines), then git apply patch.diff, which applies both hunks.

=== Page 19 ===
Tool edit: search and replace.
- The model emits an exact anchor string plus its replacement.
- Output is proportional to the change, not the file.
- Cost: fails on ambiguous, stale, or whitespace-mismatched anchors.
- Example, raise the retry count: grep -n "retries = 3" gives one unique match; replace retries = 3 with 5 in one call; read back the block and confirm the rest of the file is untouched.

=== Page 20 ===
Tool edit: structured / AST edits.
- The model names an operation on a symbol, such as rename or add parameter.
- Immune to formatting and cannot produce invalid syntax.
- Cost: per-language tooling and a limited set of expressible edits.
- Resources listed: an AST video (youtube lCrC-qojPpU) and pierce.dev notes on how language servers work.
- Example, add a timeout parameter to fetchUser(): add_param(fetchUser) with timeout default 5s; tooling rewrites the signature and all 18 callers; parse and type check confirm validity.

=== Page 21 ===
How agents apply edits (comparison of token cost against robustness, i.e., whether the edit lands where intended):
- Whole-file rewrite: drifts on long files.
- Unified diff: breaks on stale lines.
- Search/replace block: needs an exact, unique match.
- Structured/AST edit: limited language coverage.

[Figure: Two-axis trade-off chart of token cost and edit robustness, with each edit method placed on it.]

=== Page 22 ===
Tool execution: effectively a shell. It is the most powerful and most dangerous tool.
- Composition: one call can chain, filter, loop, and retry.
- Reach: filesystem, network, package managers, installed binaries.
- Persistence: files and processes outlive the individual call.
- Blast radius: whatever the shell can do, the agent can do.

=== Page 23 ===
Tool execution considerations:
- Failure signal: errors the agent can act on.
- Output: enough detail, but not too much.
- Duration: long-running and background processes.
- Budgets: when to stop retrying and hand back control.
- Isolation: where code runs and what it can reach.

=== Page 24 ===
Five more commonly used tools:
- D. Browser and visual feedback: screenshot the render and feed it back.
- A. Memory and notes: write findings to a file so plans survive compaction.
- E. Asking the user: one cheap question beats a confident wrong patch.
- B. Subagents and delegation: exploration returns a shortlist, not 40 file reads.
- C. Web search and fetch: read the installed source first, then the web.

=== Page 25 ===
Tool design best practices:
- Few, orthogonal tools. Overlapping tools make the model dither.
- Purpose-built tools. search_orders(customer_id) beats a raw run_sql tool.
- Token-cheap output: truncate, paginate, summarize. Tool design is context design.
- Errors that teach: return the fix hint, not just "invalid argument."
- Idempotent by default: safe to retry whenever possible.

=== Page 26 ===
Can we just provide the shell tool? Bar chart; the assignment will test this.
- No specialized editor: 10.3%
- Shell only: 11.0%
- Full-file view: 12.7%
- Full interaction history: 15.0%
- Purpose-built SWE-agent tools: 18.0%
- Label "No on GPT-4" appears on the chart. The axis label is not in the extracted text, but the values are presumably a success rate.

[Figure: Bar chart comparing five tool configurations, with values rising from 10.3% (no specialized editor) to 18.0% (purpose-built SWE-agent tools).]

=== Page 27 ===
Section divider: Context Management, covering prompt engineering and context engineering.

=== Page 28 ===
From prompts to agent systems (timeline):
- 2023–2024, Prompt Engineering: "How should we instruct the model?" Covers wording, examples, and output formats.
- 2025–2026, Context Engineering: "What should the model see?" Covers retrieval, memory, history, and compaction.
- 2026, Harness Engineering: "How should the agent operate?" Covers the loop, tools, sandbox, retries, and stopping.
- Now→Next, Goal Engineering: "What counts as success?" Covers objectives, criteria, constraints, and tradeoffs.
- The lecturer notes the terms are included for recognition, not endorsement.

[Figure: Timeline of four engineering eras, from prompt to goal engineering.]

=== Page 29 ===
Prompt engineering techniques: zero-shot, few-shot, role & persona, chain-of-thought, tree-of-thoughts, self-consistency, prompt chaining, meta prompting.

=== Page 30 ===
Zero-shot prompting (instruction only).
- Example: a support triage assistant classifies tickets as billing, bug, feature, or other. It replies with JSON only, e.g., {"label": ...}, and uses "other" if unclear.
- Ticket "Crashes when I export a PDF." gives {"label": "bug"}.
- Use when the task is common and the format fits in words. Move to few-shot if the rule is tacit.

=== Page 31 ===
Few-shot prompting (instruction plus examples).
- Same classification task with worked examples:
  - "Charged twice this month." → billing
  - "Can you add dark mode?" → feature
  - "asdfgh" → other
  - "Crashes when I export a PDF." → ?
- Use when the output shape is unusual or the rule is easier shown than said. Move to chain-of-thought if the task needs steps.

=== Page 32 ===
Role and persona prompting.
- Example: a senior SRE reviews a postmortem for an executive audience. Flag evidence gaps, never speculate, be direct, and use at most five bullets.
- Sample output: the timeline omits the 04:12 alert ack, which is an evidence gap, not a cause.
- Use when tone or judgment matters or the audience is specific. Move to chain-of-thought if steps are needed.

=== Page 33 ===
Chain-of-thought (make the steps explicit).
- Example: "3 features/week for 4 weeks, then 5/week for 2 weeks. Total?"
- Steps: 3 × 4 = 12; 5 × 2 = 10; 12 + 10 = 22.
- Output format: reasoning steps first, then "ANSWER: <value>" (ANSWER: 22).
- Use when the task has real steps and errors come from skipped work. Move to tree-of-thought if several paths exist.

=== Page 34 ===
Tree-of-thought (branch, score, prune).
- Example: propose 3 ways to cut checkout latency and score each 1–5 on impact and effort, then expand the best.
  - A: cache warm-up (impact 3, effort 2)
  - B: drop 3rd-party script (impact 5, effort 4)
  - C: lazy-load assets (impact 4, effort 1)
- Expand C, then B. Prune A.
- Use when several routes are plausible and can be scored cheaply. For one right answer, use self-consistency.

=== Page 35 ===
Self-consistency (sample, then vote).
- Example: same prompt sampled 5 times at T = 0.7, "Is this invoice a duplicate?" Answers: yes, yes, no, yes, yes.
- Majority is yes at 4/5 = 0.8. If the floor of 0.8 is met, accept; at 3/5, route to a human.
- Use when one right answer exists and a wrong call is expensive. For separable stages, use chaining.

=== Page 36 ===
Prompt chaining (one job per call).
- Stage 1, extract: input is email text; output is {vendor, amount, date}.
- Stage 2, validate and enrich: adds vendor_id.
- Stage 3, draft reply: output is {subject, body}.
- If a stage fails its schema, retry only that stage.
- Use when work splits into stages and each output can be validated. For prompt tuning, use meta prompting.

=== Page 37 ===
Meta prompting (the model writes the prompt).
- Example: give the current prompt, 10 test cases, and the 3 it fails. Ask for a rewrite that fixes those 3 without breaking the other 7 and returns only the new prompt.
- v2 adds an explicit refusal rule, raising the eval set from 8/10 to 10/10.
- Use when you have an eval set to score against and the prompt is what you are tuning. If gains stall, revisit your technique choice.

=== Page 38 ===
Choosing the right technique:
- Start simple: zero-shot as the baseline; few-shot for an unusual output shape or tacit rule; role and persona when tone or judgment matters.
- Add reasoning: chain-of-thought for multi-step tasks; tree-of-thought for several paths worth scoring; self-consistency for majority vote.
- Engineer the system: prompt chaining for separable stages with validated handoffs; meta prompting when the prompt itself is the artifact.

=== Page 39 ===
"Some of the techniques are already expired." Students should find out which ones in the assignment.

=== Page 40 ===
Designing prompts: four best practices.
- Example: "### Instruction ###" translating "hello!" to Spanish gives "¡Hola!" Order: instruction, delimiter, data.
- 1. Start simple, then iterate. Add context only when needed.
- 2. Partition into sections: context, instructions, tools, output spec.
- 3. Be specific and concise. Clever phrasing buys nothing.
- 4. Split big tasks into subtasks. Don't front-load complexity.
- Prompting advice is model-specific, so re-tune whenever you switch models.

=== Page 41 ===
Context engineering. A section quote from Andrej Karpathy (2025) defines it as the art and science of filling the context window with exactly the right information for the next step. Source: x.com/karpathy/status/1937902205765607626.

=== Page 42 ===
Context is a finite resource:
- Cost: every step re-sends the whole window, so every turn pays again.
- Latency: bigger prompts take longer to prefill and decode, slowing every turn.
- Attention: recall fades as the window fills, and the middle gets missed. More context does not mean better answers.

=== Page 43 ===
Length and position both affect accuracy.
- Left chart, "Simple lookup" vs. "With distractors": accuracy decays as input tokens grow. Labeled values include 73%, 40%, 46%, 60%, 80%, and 100%.
- Right chart, answer accuracy by position among 20 documents: 1st 76%, 5th 61%, 10th 55%, 15th 59%, 20th 71%. Accuracy is lowest in the middle.
- Sources: Context Rot (Chroma); Liu et al., "Lost in the Middle," TACL 12 (2024).

[Figure: Two line charts. Left shows accuracy declining with input tokens, for simple lookup and with distractors. Right shows a U-shaped curve of accuracy by document position, with the middle lowest.]

=== Page 44 ===
Anatomy of the context window: system prompt, tool definitions, retrieved context, message history, user + LLM + tool-call results, and project environment.
- Illustrative token budget for one agent turn: about 2K, 6K, 25K, 8K, and 80K+ and growing. The extracted text does not pair these values with specific components.
- Question posed: what to do when context becomes too large?

[Figure: Stacked token-budget bar for one agent turn, with the window filling up across the components.]

=== Page 45 ===
Managing the context window. Four strategies: admission, offloading, transformation, compaction. They range from preventive and lossless to lossy and irreversible.

=== Page 46 ===
(no extractable text — image-only slide)

=== Page 47 ===
Admission: guard what enters the window.
- Targeted retrieval: query narrowly and fetch fields, not documents.
- Tool output shaping: drop the DOM and keep the extract.
- Truncation: cap size only when shaping can't.
- Isolation: hand the raw payload to a subagent.
- Example: raw DOM of 48,000 tokens becomes an extract of prices and headings at 900 tokens, which is 98% smaller with the same answer.

[Figure: Before and after bars showing a 48,000-token raw DOM shrinking to 900 tokens.]

=== Page 48 ===
Offloading: don't load until needed.
- Progressive tool definition: load schemas only when needed.
- Tool search: keep an index and fetch on demand.
- Tool output offload: return a handle and load on demand.
- Externalized task list: keep the plan on disk.
- Persistent memory: write notes out and keep a small index.
- Example: 60 schemas resident at 42,000 tokens become an index plus 3 schemas at 3,100 tokens, which is 93% smaller with all 60 still reachable.

[Figure: Before and after bars showing 60 tool schemas at 42,000 tokens shrinking to an index plus 3 schemas at 3,100 tokens.]

=== Page 49 ===
Transformation: selectively drop history.
- Deduplication: keep the newest state of each object.
- Observation masking: strip tool results older than N steps.
- Sliding window: keep only recent turns and the head.
- Example: every result kept at 96,000 tokens becomes the newest state at 24,000 tokens, which is 75% smaller with nothing summarized.

[Figure: Before and after bars showing 96,000 tokens reduced to 24,000 through masking and dedup.]

=== Page 50 ===
Compaction: the LLM as a last resort.
- Rolling summary: summarize old tool results as you go.
- Full summary: rewrite the whole history at the limit.
- Warnings: reserve headroom for output, preserve the system prefix, and re-inject critical facts afterward.
- Auto memory: persist key facts outside the window.

[Figure: Before and after diagram. At the limit, history fills the window. After LLM compaction, a summary replaces old results and headroom is restored.]

=== Page 51 ===
Five ways context fails (Breunig, "How Contexts Fail and How to Fix Them," 2025):
- Poisoning: a hallucination enters the window and is later cited as fact.
- Distraction: history grows until the agent imitates its own past actions.
- Confusion: irrelevant tools or documents steer the answer off course.
- Clash: new information contradicts old, and both stay unresolved.
- Drift: the real goal is buried and swapped for a nearby subgoal.
- Naming the failure makes the fix obvious.

=== Page 52 ===
Agent = Model × Harness. Model capability sets the ceiling; the harness determines realized performance.

=== Page 53 ===
Changing the harness improves accuracy about 2× (table, resolved tasks):
- SWE-bench Verified: basic harness 43/169 → improved harness 72/169.
- SWE-bench Pro: basic harness 31/316 → improved harness 72/316.
- Improvements: old tool outputs compacted, recent observations kept visible, repetition and stalls detected, interventions when stuck.
- Takeaway: some apparent model failures are actually context and control-loop failures.
- Source: Lewis, S., "Same Model, Different Harness: Different Coding-Agent Results" (arXiv 2608.26218, 2026).

=== Page 54 ===
Agent = Model × Harness, as an assignment experiment. Agent loop, prompt, tools, context management, and failure handling all matter.

=== Page 55 ===
Next class:
- Agent design II
- Agent (persistent) memory
- Cost-effective agents
- Safety and security
- Multi-agent designs

=== Page 56 ===
Optional reading: "Beyond the ReAct Loop."
- ReAct loops every step: Thought → Act → Observe.
- Reflexion loops after a failure: Attempt → Evaluate → Critique → Retry.
- Plan-and-execute loops on deviation: Plan → Execute steps → Re-plan.
- Tree search has no loop and makes one wide pass: State → Branch A/B/C → keep best. Branches are explored in parallel and only one survives.
- Legend: model call, app/tool action, chosen outcome.

[Figure: Four loop diagrams (ReAct, Reflexion, plan-and-execute, tree search) with a legend for model calls, app/tool actions, and chosen outcomes.]

TOTAL PAGES: 56
