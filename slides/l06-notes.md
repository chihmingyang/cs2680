# L06 slides 逐頁筆記

- 來源：https://cs2680.com/slides/6_agent_design_3.pdf
- 頁數：31（PDF 檢視器的頁數，封面 = 1；與 docs/l06.html 的 data-pages-total 一致）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。
- 頁碼校正：WebFetch 把 slide 右下角的 footer 號碼當頁碼，footer 會跳號（隱藏的 slide）。本檔已換算成 PDF 頁數。 跳過的 footer 號碼：[1, 19]。
  footer → PDF：2–18 → 1–17；20–33 → 18–31

=== Page 1 ===
Title: "Modern AI systems: agents and system optimizations." Presenter: Juncheng Yang. Lecture: "Agent design III: memory, and reliability." Course: Harvard MaDSys, course.agentic-system.org.

=== Page 2 ===
Title: Logistics.
- Office hour this Thursday, 3:30pm, SEC 4.308.
- Final project poster presentation: 9am-1pm, Dec 7. Students should reach out this week if the time does not work.
- AI-generated reference materials at cs2680.com/notes/agent-evaluation. The reading list is curated by the instructor, and the notes are reviewed by the instructor and TAs.

=== Page 3 ===
Title: Plan for today.
- Multi-agent design (continued from last lecture).
- Agent memory.
- Agent reliability.

=== Page 4 ===
(no extractable text — image-only slide)

=== Page 5 ===
Title: Agent memory. Subtitle: persistent state beyond the context window.
- Diagram: User → Agent Harness → LLM. The harness connects to a Memory Store.
- Context window = temporary working state.
- Memory store = persistent state across interactions.
- [Figure: Architecture diagram showing the harness sitting between the user, LLM, context window (temporary), and memory store (persistent).]

=== Page 6 ===
Title: Agent memory design questions. Each question maps to a policy stage:
- Who owns the memory?
- Is it worth keeping? → WRITE OR SKIP decision.
- What should it become? → ENCODE / ORGANIZE format.
- Does this task need it? → RETRIEVE.
- What broader lesson follows? → REFLECT / GENERALIZE lesson.
- Is it still valid? → KEEP / UPDATE / DELETE status.
- Where should it live? → STORE backend.
- Navigation bar lists these six concerns: Keeping, Format, Backend, Need it, Lesson, Valid.

=== Page 7 ===
Title: Decision: when should something become memory? Trade-off: writing every interaction raises recall but adds noise.
Approaches, ordered from high recall to high precision:
- Write every interaction (high recall).
- Periodic LLM review.
- Small classifier.
- Deterministic rules (heuristics).
- Explicit user request (high precision).
- Grouped as "write every interaction" at one end and "selective writing" at the other.

=== Page 8 ===
Title: How to organize the memory? Four representations:
- Raw events/episodes. Example: "We moved serving from vLLM to SGLang." High fidelity, but large and redundant.
- Unstructured summaries. Example: "Uses SGLang for model serving." Compact, but may lose context.
- Structured state. Example: {"serving_engine": "SGLang", …}. Queryable, but the schema constrains it.
- Knowledge graph. Example: Project → USES → SGLang. Linked entities; can represent change over time.
- Slide marked "Hands up" (audience poll).

=== Page 9 ===
Title: How to store the memory? Four backends:
- Plain files (CLAUDE.md, scratchpad): simple to inspect, diff, and search.
- Key-value or relational database (Redis, SQLite, Postgres JSONB): exact lookup, filtering, transactions.
- Vector store (pgvector, Chroma, Pinecone): exact or approximate similarity search.
- Graph database (Neo4j, FalkorDB via Graphiti): relationship queries and multi-hop traversal.
- Slide marked "Hands up."

=== Page 10 ===
Title: When should memory be used? Three control policies:
- Automatic: every turn runs search → LLM → add. Pro: predictable and simple. Con: adds latency and irrelevant context.
- Runtime-controlled: code checks if memory is needed (search) and if something is memorable (add). Pro: selective and efficient. Con: needs rules or a classifier.
- Model-controlled: the LLM calls search_memory(), add_memory(), update_memory(), forget_memory(). Pro: demand-driven. Con: may miss useful reads or writes.
- Note: many systems use a hybrid; read and write policies may differ.

=== Page 11 ===
Title: How to retrieve the memory? Semantic relevance is only one retrieval signal.
- Basic pipeline: Query → Vector search → Top-k memories → Prompt.
- Additional signals:
  - Semantic match: meaning matches the query.
  - Scope: same user, project, entity, or task.
  - Importance: cost of missing or including it.
  - Validity: true for this task at this time.
  - Provenance: source, confidence, and evidence.

=== Page 12 ===
Title: How to generalize from observations? Example: the agent was asked about vLLM, SGLang, TRT-LLM, and LLM scheduling. A reflection step produces: "Hypothesis: frequent interest in LLM inference systems," with confidence "medium."
- When should consolidation happen?
  - After enough new evidence (every N events or when context fills).
  - When facts conflict or repeat.
  - In a background job when possible.

=== Page 13 ===
Title: Forgetting is a first-class memory operation.
- Lifecycle controls: mark invalid; erase permanently; expire after a TTL; create tiers and evict from active memory.
- Reasons to forget: stale information; incorrect or conflicting information; privacy and security; storage and retrieval cost.

=== Page 14 ===
Title: Memory needs valid time and provenance.
- Timeline example:
  - April 2026: "Project serves models with vLLM." Status: superseded.
  - June 2026: "Project serves models with SGLang." Status: current.
- Source: Episode 28, "We moved serving from vLLM to SGLang." Extracted fact: Project → SERVES_WITH → SGLang, with source Episode 28.
- Definitions: valid time = which fact applied when; provenance = where the fact came from.
- [Figure: Timeline with two dated memory entries, one superseded and one current, linked to a source episode.]

=== Page 15 ===
Title: Who owns the memory? Two models:
- Agent-owned: files in the harness (CLAUDE.md, agent scratchpad, task notes). The harness persists memory to disk. Diagram: agent harness reads/writes CLAUDE.md and task notes.
- Dedicated memory system: a service the agent calls (Mem0, Graphiti, supermemory). The harness calls a memory layer (library or service) to search and update memories. Memory is an API shared across agents and sessions.
- [Figure: Two architecture diagrams comparing file-based memory in the harness with an external memory layer accessed via API.]

=== Page 16 ===
Title: Dedicated memory systems (three examples):
- Mem0: fact-centric. Input: messages, scoped by user, agent, or run. Retrieval: vector search with filters; optional graph memory. Example: "Uses SGLang for model serving."
- Graphiti: temporal knowledge graph. Input: episodes that yield entities and time-aware facts. Retrieval: hybrid semantic, keyword, and graph search. Example: uses → SGLang, valid Apr 2026 → present.
- supermemory: profile, memory, and document. Maintains a user profile alongside memory and documents. Input: conversations linked to source and time. Retrieval: profile, memory, and document search.

=== Page 17 ===
Title: Agent memory design checklist. Seven stages, each with a guiding question:
- Observe: Is this worth remembering?
- Select: What is useful for the current task?
- Encode/organize: What representation preserves the needed meaning?
- Store: Where should it live (file, database)?
- Retrieve: What is useful for the current task? (Shown alongside Select.)
- Reflect/consolidate: Does this update or contradict an old memory?
- Forget: When is information stale or irrelevant?
- Takeaway: each stage is a policy decision.

=== Page 18 ===
Title: Failure modes. Eight listed:
- Retrieval miss: relevant memory exists but isn't found.
- Context pollution: too many irrelevant memories enter context.
- Memory hallucination: an inference is stored as fact. Example: "studying at Harvard" becomes "visiting student at Harvard."
- Staleness: an old fact overrides newer information.
- Isolation failure: memory crosses a user boundary.
- Overgeneralization: one event becomes a durable preference.
- Persistent prompt injection: untrusted content returns later as instructions.
- Unbounded growth: size grows with lifetime, degrading retrieval cost and quality.

=== Page 19 ===
Title: How to evaluate agent memory. Metrics by category:
- Writes and updates: precision, recall, stale-memory rate.
- Retrieval: precision, recall.
- System: latency, token overhead, store growth.
- Governance: deletion compliance and scope isolation.

=== Page 20 ===
Title: Agent memory evaluation. Three benchmarks:
- LoCoMo: 1,540 questions; 10 long dialogues. (ACL 2024)
- LongMemEval: 500 questions; 5 memory abilities. (ICLR 2025)
- BEAM: 2,000 questions; up to 10M tokens. (ICLR 2026)
- Also listed: LoCoMo-Refined.
- Purpose: mainly test whether an agent can recall and reason over user-assistant histories. Coverage includes recall, temporal reasoning, updates, preferences, and abstention.

=== Page 21 ===
Title: The agent memory stack. Two patterns:
- Separate memory layer: agent runtime (Claude Code, Letta, Codex) → memory management (Mem0, Letta built-in, custom) → storage (vector, SQL, graph, object stores).
- Memory inside the harness: agent runtime (Claude Code, Letta, Codex) → memory management in the runtime → storage as markdown files.
- A "?" marks an unresolved question about which pattern fits.

=== Page 22 ===
Title: Why is agent reliability a problem? Errors compound.
- Key stat: 1 in 13 50-step runs finish with no errors. A run succeeds only if every step does; real runs are worse than this estimate.
- [Figure: Line/bar chart of "Chance an agent run is error-free" versus number of steps in the trajectory, assuming 95% success per step.]
  - 1 step: 95%
  - 5 steps: 77%
  - 10 steps: 60%
  - 20 steps: 36%
  - 50 steps: 8%
- Footnote: assumes each step succeeds independently with probability 0.95.

=== Page 23 ===
(no extractable text — image-only slide)

=== Page 24 ===
Title: Agent reliability. Question: what are the ways agents fail, and where does the fault originate? Five sources:
- User/task specification: was the goal unambiguous? (specification failure)
- Agent harness: context, loop, scheduling. (harness failure)
- LLM: reasoning and planning. (model failure)
- Tool layer: shell, browser, APIs. (tool failure)
- Environment: repo, OS, web, services. (environment failure)

=== Page 25 ===
Title: Task specification failures. Columns: failure, what the spec said, what the agent did, the fix.
- Ambiguous goal: "Fix the login bug" → fixed the wrong one of three. Fix: name the file, symptom, and repro.
- Proxy objective: "Make the tests pass" → deleted the failing test. Fix: forbid test edits; review the diff.
- Unstated constraint: "Speed up search" → broke the public API. Fix: state what must not change.
- No definition of done: "Clean up the parser" → never stopped refactoring. Fix: give an exit test and a stop rule.
- Conflicting goals: "Minimal diff, every edge case" → silently dropped the edge cases. Fix: rank the goals explicitly.

=== Page 26 ===
Title: Agent harness failures. Columns: failure, what the harness did, effect, fix.
- Context truncation error: trimmed the oldest turns → forgot the "keep the API" rule. Fix: pin key rules outside the window.
- Memory error: recalled a stale note as fact → edited a file that had moved. Fix: date memories; re-check before use.
- State corruption error: kept a half-applied edit → later steps built on broken files. Fix: checkpoint; roll back failed steps.
- Control loop error: no step or cost budget → 200 steps, no progress. Fix: cap steps, cost, and time.
- Blocking fan-out: waited on every sub-agent → one slow child stalled the run. Fix: set timeouts; use partial results.

=== Page 27 ===
Title: Model failures. Columns: failure, what the model reasoned, what the agent did, the fix.
- Hallucination: "requests.fetch() exists" → called a nonexistent function. Fix: check calls against real docs.
- Instruction violation: "Speed matters more than the API" → changed a signature it was told to keep. Fix: restate constraints; check the diff.
- Faulty reasoning: "A timeout means the network is down" → added retries to a deadlock. Fix: test the hypothesis before fixing.
- Reasoning–action mismatch: "I'll only touch parser.py" → rewrote three other files. Fix: compare each action to the plan.
- Unverified success: "Tests probably pass now" → declared done, ran nothing. Fix: require test output as proof.
- Long-horizon degradation: "The config still needs fixing" → undid its own fix from step 12. Fix: re-read state; split into short tasks.

=== Page 28 ===
Title: Tool failures. Columns: failure, what the tool returned, what the agent did, the fix.
- Truncated output: first 100 lines of a log → missed the error on line 4,000. Fix: return errors first; allow paging.
- Silent failure: exit 0, empty result → assumed no matches. Fix: separate "empty" from "failed."
- Ambiguous schema: a date with no time zone → scheduled the job 8 hours off. Fix: use typed, explicit schemas.
- Flaky call: timeout on first try → declared the service down. Fix: retry with backoff before judging.
- Misleading error: "Permission denied" on a typo → retried with sudo. Fix: return precise, actionable errors.

=== Page 29 ===
Title: Environment failures. Columns: failure, what the environment had, what the agent did, the fix.
- Stale state: yesterday's cached build → passed tests on old code. Fix: build clean from a fresh cache.
- Version mismatch: Python 3.8, not 3.12 → shipped code that crashed. Fix: pin versions in a lockfile.
- Random failure: task success depended on environment → failed because of a leap year. Fix: rerun failures; quarantine flakes.
- Changed web page layout: redesigned checkout page → clicked the wrong button. Fix: re-read the page before acting.
- Rate limit: HTTP 429 after 50 calls → stopped mid-migration. Fix: throttle and checkpoint long jobs.

=== Page 30 ===
Title: Designing for failure. Five areas, each with mitigations:
- Task specification: write "done" as a test. Use acceptance tests up front; list what must not change.
- Agent harness: bound every run. Use step, cost, and time caps; checkpoint and roll back.
- Model: demand evidence. Require proof for every claim; verify; use stronger models.
- Tool: fail loudly. Use typed schemas; keep errors distinct from empty results.
- Environment: pin and isolate. Use fresh, pinned sandboxes; retry flakes before judging.
- Closing takeaway: "We do not yet understand agents at scale, and there is little formal best practice."

=== Page 31 ===
Title: Next class.
- Agent evaluation.
- Cost-effective agents.
- Case studies.

TOTAL PAGES: 31
