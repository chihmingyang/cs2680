# L05 slides 逐頁筆記

- 來源：https://cs2680.com/slides/5_agent_design_2.pdf
- 頁數：46（PDF 檢視器的頁數，封面 = 1）；文字抽取只確認到 45 頁有內容，第 46 頁未能確認（見下方「頁碼說明」）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。

頁碼說明（2026-10-19 整理時的觀察，供對照 PDF 時核對）：

- 每張 slide 右下角有印刷編號（"Harvard MaDSys · course.agentic-system.org K"）。封面印 2，所以多數頁「印刷編號 = PDF 頁碼 + 1」。每頁第一行標 `(footer K)` 方便對照。
- 印刷編號 32、33、34、46 在抽取文字裡不存在。p.31「Messages should carry semantics」和 p.32「Communication: the design space」在抽取文字裡只共用一個印刷編號 35，這裡依現有文章 `docs/l05.html` 的用法拆成兩頁。
- 從 p.31 起，頁碼沿用 `docs/l05.html` 目前的引用（p.33 = 分散式問題例子、p.36 = black-box LLM、p.38 = agent card、p.40 = lifecycle、p.42 = MCP、p.43 = MCP vs A2A、p.44 = design principles）。若 PDF 實際在 MCP（p.42）之後還有一張無文字的頁（印刷編號 46），p.43–p.46 要各往後移一頁。需要有人開 PDF 核對一次。

=== Page 1 ===
(footer 2) Cover. Title: "Modern AI systems: agents and system optimizations". Presenter: Juncheng Yang. Session title: "Agent Design II: Multi-Agent Systems". Course footer: Harvard MaDSys · course.agentic-system.org.

=== Page 2 ===
(footer 3) Logistics.
- Claude Code Premium seat
- Assignment 1: Canvas, repo url, mini product
- "Assignment 2 is waiting for you, due in ~two weeks"
- Office hour next Thursday 3:30-5pm, SEC 4.308
- Pre-proposal

=== Page 3 ===
(footer 4) Plan for today.
- Multi-agent design
  - Architecture
  - Coordination: task decomposition
  - Communication
- Agent memory

=== Page 4 ===
(footer 5) (no extractable text) Only the course footer is present. Likely a section-divider or image-only slide.
[Figure: image-only page; content not recoverable from text extraction.]

=== Page 5 ===
(footer 6) From one agent to many.
- Three sub-topics for this part: Architecture, Coordination, Communication.
- Multi-agent systems have decades of prior research; this lecture will not cover that history.

=== Page 6 ===
(footer 7) When and why split work across agents? Four reasons:
- specialization: different models, prompts and tools
- isolation: give different agents different privileges
- parallelism: independent subtasks execute concurrently
- context management: don't give every agent the entire trajectory
- "Hands up" cue on the slide (audience prompt).

=== Page 7 ===
(footer 8) Three questions / graphs behind every architecture.
- Control graph: who coordinates? One supervisor, a hierarchy, or nobody. Can change at runtime (handoff).
- Communication graph: how do agents talk? Direct messages, broadcast, or a shared workspace.
- Task graph: how is work decomposed? Up front by a planner, by bidding, or emergently from local rules.

=== Page 8 ===
(footer 9) Multi-agent architecture. Numbered list of the eight patterns covered next:
1. Supervisor–worker
2. Hierarchical
3. Pipeline / DAG
4. Blackboard
5. Committee
6. Market
7. Swarm
8. Dynamic topology

=== Page 9 ===
(footer 10) 1. Supervisor–worker.
- One agent plans, delegates and integrates; workers see only their subtask.
- Best when subtasks are independent and can run in parallel.
- Weakness: the supervisor is a bottleneck. It re-reads every result, and its context grows fastest.
- Profile: Task = supervisor splits work up front. Control = one supervisor. Comms = star topology via the supervisor.
[Figure: a Supervisor box connected to three workers: Researcher, Coder, Reviewer.]

=== Page 10 ===
(footer 11) 2. Hierarchical agents.
- Supervisor–worker applied recursively: supervisors manage sub-supervisors.
- Fits tasks that already decompose hierarchically, e.g. storage, query engine, testing.
- Challenge: where decomposition happens, and how much context crosses each boundary.
- Profile: Task = split again at each level. Control = nested supervisors. Comms = tree, parent–child only.
- Example: feature build.
[Figure: tree with Feature manager at top; Backend lead (children: API, Database) and Frontend lead (children: UI, E2E tests).]

=== Page 11 ===
(footer 12) 3. Pipeline / DAG.
- Fixed stages with a typed contract at each boundary.
- Cheapest topology to debug: errors localize to a stage.
- Weakness: no path backwards. Stage four cannot ask stage one for a better source.
- Rule of thumb: one retry edge beats one more agent.
- Example: invoice processing.
- Profile: Task = stages fixed at design time. Control = the order is the control. Comms = stage to stage.
[Figure: linear chain OCR → Extract fields → Match to PO → Approve → Post to ledger.]

=== Page 12 ===
(footer 13) 4. Blackboard and shared memory.
- Agents coordinate through shared state instead of direct messages.
- The workspace can be a database, vector store, filesystem, Git repo or task graph.
- Profile: Task = emerges from shared state. Control = no central controller. Comms = indirect, via the workspace.
- Agents can join or leave without rewiring. Shared state is durable and inspectable.
- Challenges: consistency, concurrency control, provenance, versioning, garbage collection.
- Example: agents sharing a Git repo.
[Figure: central "Git repository" box (task list, commits, history) connected to Feature agent, Refactor agent, Test agent.]

=== Page 13 ===
(footer 14) 5. Committee / debate.
- Agents propose and discuss; a judge or a vote resolves disagreement.
- Example: essay grading.
- Profile: Task = one task, repeated in parallel. Control = the judge decides. Comms = peers, then to the judge.
- Improves accuracy on judgment-heavy tasks.
- Failure mode: agreement without independence. Same model and context means the same blind spot.
[Figure: a Judge above Grader A and Grader B.]

=== Page 14 ===
(footer 15) 6. Market and auction.
- Agents bid for announced tasks based on capability, cost and latency.
- Heterogeneous agents: different models, tools, machines, cost, expertise.
- Example: GPU job router, rule "cheapest bid under 5s wins". Question: "Who can run this training job?"
  - A100 node: $0.20, ETA 3s
  - T4 node: $0.05, ETA 10s
  - H100 node: $0.40, ETA 1s
  - Result: job goes to the A100 node (T4 is cheaper but misses the 5s limit; H100 is faster but costs more).
- Profile: Task = announced, claimed by bid. Control = auctioneer clears. Comms = broadcast out, bids back.
- Work goes to the cheapest capable agent without a central planner.
- Weakness: bids are self-reported; an agent can win by overstating its abilities.
[Figure: three node cards, each showing price and ETA, with the winning A100 bid highlighted.]

=== Page 15 ===
(footer 16) 7. Swarm.
- No permanent coordinator; agents negotiate and exchange findings directly.
- Needs protocols for discovery, addressing, synchronization, termination and trust.
- Example: warehouse robots negotiating which picker takes which order.
- Benefit: no coordinator to bottleneck or fail; work continues as peers drop in and out.
- Weakness: communication is O(n²); conflict resolution is hard. Rarely used in products.
- Profile: Task = negotiated locally. Control = no permanent coordinator. Comms = all-to-all, O(n²).
[Figure: four peers Picker 1–Picker 4, each connected to every other.]

=== Page 16 ===
(footer 17) 8. Dynamic topology.
- Agents are added, removed or rewired while the task runs.
- Example: a support bot adds billing and log agents only when a ticket escalates.
- Profile: Task = re-split as work gets hard. Control = shifts as agents join. Comms = dynamic at runtime.
- Benefit: capacity scales with difficulty; simple tickets stay cheap.
- Weakness: every run takes a different shape, so failures are hard to reproduce.
[Figure: left "Routine ticket" = one Support bot; right "After escalation" = Support bot with Billing agent and Log agent attached.]

=== Page 17 ===
(footer 18) Real systems are hybrids.
- Production systems combine patterns: hierarchy, shared memory, pipeline, and re-planning if needed.
[Figure: Supervisor above a Planner agent, which emits a "Dynamic task DAG" feeding Coder, Researcher, Tester and Reviewer agents; a "Shared Git" box connects to them. Labels: "Combines hierarchy / shared memory / pipeline / re-plan if needed".]

=== Page 18 ===
(footer 19) Eight architectures — summary table. Columns: Category | Architecture | Core idea | Best for | Weakness.
- Centralized | Supervisor–worker | One planner, many workers | Separable subtasks | Planner bottleneck
- Centralized | Hierarchical | Supervisors of supervisors | Recursive splits | Errors amplify
- Centralized | Pipeline / DAG | Each stage feeds the next | Clear ordered stages | Errors propagate
- Centralized | Market / auction | Agents bid for tasks | Dynamic allocation | Bad bids
- Decentralized | Blackboard | Shared workspace | One shared artifact | Stale state
- Decentralized | Committee / debate | Answer, then reconcile | Judgment calls | Groupthink
- Decentralized | Swarm | Direct talk, no controller | Local negotiation | O(n²) messages
- Hybrid | Dynamic topology | Rewires as work proceeds | Unknown structure | Hard to debug
(Category labels follow the row grouping seen in the extracted text.)

=== Page 19 ===
(footer 20) Task decomposition (section opener).
- Idea: split a complex task into subtasks, then merge the results.
[Figure: "Complex task" fans out to Sub-task 1, Sub-task 2, Sub-task 3, which converge into "Merged result".]

=== Page 20 ===
(footer 21) Task decomposition — ways to split.
- Data: each agent handles a subset of documents or records.
- Expertise: security, performance, correctness, legal analysis.
- Stage: plan, implement, test, review.
- Hypothesis: agents investigate competing explanations.
- Tool: web, database, code execution, internal documents.
- Authority: agents act in different administrative domains.
- Example: a 200-file PR split first by data (files), then by expertise (security, performance).

=== Page 21 ===
(footer 22) Things to consider when creating sub-tasks. Eight-item checklist:
- Objective
- Inputs and relevant context
- Boundaries and exclusions
- Available tools and permissions
- Expected output schema
- Completion test
- Budget and deadline
- Dependencies
- Poor sub-task: "Research storage systems".
- Better sub-task: "Identify storage-related papers published in 2026; return title, date, system contribution, evaluation scale and primary-source URL; exclude database query optimization".

=== Page 22 ===
(footer 23) Granularity tradeoff.
- Tasks too large: little parallelism; the work stays sequential.
- Tasks too small: scheduling and communication overhead dominates.
- Formula: T_multi ≈ T_planning + T_critical path + T_communication + T_merge.
- Parallelism pays off only when the saved sequential work exceeds planning, communication and integration costs.
- Example: 20 one-line lookups batched into 4 subtasks to keep overhead below the gain.

=== Page 23 ===
(footer 24) Static versus dynamic decomposition. Four modes:
- Static: known before execution; predictable and easy to evaluate. Example: summarize each of five uploaded PDFs.
- Dynamic: agents create new tasks in response to discoveries. Example: a dead link spawns a lookup task.
- Recursive: workers may delegate further. Example: a review agent spins up one subagent per subfield.
- Opportunistic: idle agents claim newly available tasks. Example: an idle agent picks up the next unlabeled document.
- Warning: decomposition needs spawning limits, budgets, depth limits and termination conditions. "Without them, delegation explodes recursively."

=== Page 24 ===
(footer 25) Common decomposition failures (01–04).
- 01 Overlap: two agents summarize the same paper. [Figure: Agent A and Agent B both pointing at one paper.]
- 02 Gap: "2020–2023" plus "2025–2026" skips 2024. [Figure: timeline labeled 2020–23, 2024 (gap), 2025–26.]
- 03 Hidden dependency: Pricing needs Sizing, found only at run time. [Figure: Sizing → Pricing dependency arrow.]
- 04 Unmergeable outputs: one agent returns unstructured text, another returns JSON; "Merge fails". [Figure: "Unstructured" and "JSON" boxes feeding a failed merge.]

=== Page 25 ===
(footer 26) Common decomposition failures, continued (05–06).
- 06 Straggler: six agents finish in 20s, one takes 4 minutes. [Figure: bars labeled 20s, 25s and 4 min.]
- 05 Lost global context: every section is fine; the report contradicts itself. [Figure: "§1 ✓ §2 ✓ §3 ✓" leading to "Whole report ✗".]

=== Page 26 ===
(footer 27) Agent communication (section opener).
- Example flow: User → Research Agent → (Web Agent, Coding Agent, Data Agent) → Final answer.
[Figure: User at top, Research Agent in the middle, three specialist agents below it, Final answer at the bottom.]

=== Page 27 ===
(footer 28) Four dimensions of multi-agent communication.
- Topology: who can talk to whom? supervisor–worker or peer-to-peer; determined by the architecture.
- Medium: how is information exchanged? messages, shared memory, files, database.
- Format and semantics: how is a message structured and what does it express? delegate, report, ask, handoff, cancel.
- Channel: how is information passed? p2p, broadcast, pub–sub, shared state, request–response.

=== Page 28 ===
(footer 29) Communication medium. Three options:
- Message passing: agents send explicit messages over a queue or bus. Example: a coder posts a result to the orchestrator's inbox.
- Shared memory: one in-process state object that all agents read and write. Example: a shared task list updated as work completes.
- Files and artifacts (including DB): work products handed over through a file store. Example: a researcher writes notes.md; the writer opens it.

=== Page 29 ===
(footer 30) Communication channels. Six options, each with an example:
- Direct point-to-point messages: planner hands a task spec to the coder agent.
- Broadcast: orchestrator tells every agent the build failed.
- Publish–subscribe: agents subscribe to a "new ticket" topic and react.
- Shared blackboard: agents read and write one shared findings scratchpad.
- Request–response: an agent queries a retrieval agent and waits for documents.
- Artifact passing: one agent writes report.md; the next reads it.

=== Page 30 ===
(footer 31) Message format.
- Natural language: flexible, but ambiguous.
- Structured messages: easy to validate, less expressive.
- "A practical design uses both."
- Example JSON result message:
  {"task_id": "T17", "type": "result", "status": "complete", "claim": "The regression began after commit X", "confidence": 0.82, "evidence": ["log:2391", "commit:X"], "artifact": "analysis/T17.json", "requires_response": false}

=== Page 31 ===
(no footer number extracted; shares printed footer 35 with p.32 in the text extraction) Messages should carry semantics.
- Principle: natural language for content, structured protocol for coordination. Separate control from content.
- Bad: everything in one string, e.g. {"message": "some text"}.
- Good: an envelope — {"id": "msg-381", "task_id": "t-17", "from": "planner", "to": "researcher", "type": "DELEGATE", "payload": { ... }}.
- Operations the runtime knows: DELEGATE, QUERY, REPORT, HANDOFF, UPDATE, CANCEL, ACK, ERROR, COMPLETE (nine).
- "The runtime can route, retry and stop without asking an LLM what the message meant."

=== Page 32 ===
(footer 35) Communication: the design space. Table — Dimension | Options | Rule of thumb:
- Topology | supervisor–worker, peer-to-peer, mesh | Mirror the task's dependencies
- Medium | messages, shared memory, files | One medium per link
- Channel | p2p, broadcast, pub–sub, request–reply | Broadcast only when all must know
- Format | natural language + control fields | Route on the fields, not the prose
- Takeaway: "Every choice trades latency, context or reliability."

=== Page 33 ===
(footer 36) Communication is a hard distributed systems problem.
- Scenario: Agent A sends "purchase 8 GPU instances" to Agent B. Network timeout — no reply. Did B execute the action?
- Questions: retry or give up? at-most-once or at-least-once? is exactly-once even available?
- Mitigations: idempotency key based on task_id; a compensation / rollback path; decide who pays for a double purchase.
[Figure: Agent A and Agent B lifelines; arrow "purchase 8 GPU instances" from A to B; reply marked "network timeout — no reply".]

=== Page 34 ===
(footer 37) Distributed systems are hard. Six classic problems:
- Partial failure: you cannot tell a slow agent from a dead one.
- Concurrency and non-determinism: many machines modify state at once.
- Consistency among replicated states: tradeoff among consistency, availability, partition tolerance and latency.
- No global clock: clocks on different machines disagree.
- Unreliable network: packets can be delayed, dropped, reordered or duplicated.
- Debugging and observability: many requests, distributed logs with clock drift.
- Multi-agent systems inherit these problems.

=== Page 35 ===
(footer 38) More challenges when the system runs multiple agents.
- Scheduling: who runs next, and for how long.
- State management: checkpoints, memory, provenance, versioning.
- Resource allocation: models, CPU and other shared resources.
- No predetermined request flow: the system cannot know who will need to run, for how long, or how many resources each agent will consume.

=== Page 36 ===
(footer 39) Even harder when you consider the black-box LLMs! Two groups:
- Context problems:
  - Information loss: summaries drop what the worker knew.
  - Context pollution: what matters gets buried.
  - Stale information: B still acts on X=3 after X changed to 5.
  - Conflicting beliefs: A says "safe", B says "vulnerable".
- Coordination and communication problems:
  - Observability and failure diagnosis: "Why did it fail?"
  - Lost ownership: each agent assumes another owns the task.
  - Communication loops: A asks B, B asks C, C asks A.

=== Page 37 ===
(footer 40) A2A: agent → agent (agent-to-agent protocol).
- Four steps between Agent A and Agent B: (1) discover capabilities, (2) send message, create task, (3) progress updates, (4) return artifact.
- Example question: "Analyze whether company X should move its inference stack to GPUs Y."
- Example agents: Research Agent (coordinator; finds peers via their Agent Cards), Finance Agent (estimate GPU cost), Search Agent (find benchmark data), Coding Agent (run these benchmarks).
[Figure: sequence diagram with Agent A and Agent B lifelines and the four labeled arrows; beside it, the Research Agent linked to Finance, Search and Coding agents.]

=== Page 38 ===
(footer 41) A2A agent card.
- Each A2A server publishes a machine-readable card for discovery and capability description.
- Example card: "name": "Travel Agent"; "description": "Plans business travel"; "skills": [{"id": "book-flight"}]; "supportedInterfaces": [...]; "capabilities": {"streaming": true}; "securitySchemes": {...}.
- Fetched via GET /.well-known/agent-card.json.
- What a caller learns: Identity (who the agent is); Skills (what it claims it can do); Endpoints (where and how to call); Capabilities (streaming, push); Auth (which security scheme to satisfy).
[Figure: JSON code block of the card with the GET request line below it.]

=== Page 39 ===
(footer 42) Three A2A abstractions.
- Message: one turn between client and agent. Example: "Book a flight to Boston".
- Task: a stateful unit of work with an ID and a lifecycle. Example: task-42: working → completed.
- Artifact: output the task produces. Example: itinerary PDF, booking data.
- A message starts a task; the task returns artifacts. Follow-ups join the same task: "Which date?" → "Oct 3".
[Figure: Message —starts→ Task —returns→ Artifact.]

=== Page 40 ===
(footer 43) A2A task lifecycle.
- A2A is a stateful task protocol: work can pause for input or auth, then resume.
- States: Submitted, Working, Input required, Auth required, Completed, Failed, Rejected, Canceled.
- Example: "Book a flight" → Input required ("Which date?") → "Oct 3" → Working again.
[Figure: state diagram. Submitted → Working. Working ↔ Input required and Working ↔ Auth required. Terminal states: Completed, Failed, Rejected, Canceled. Not every arrow is labeled on the slide.]

=== Page 41 ===
(footer 44) Following a long-running task.
- "Tasks can run for seconds or hours; the caller picks how to track them."
- Polling: client re-checks until done. Use for short jobs.
- Streaming: live updates. Use for interactive output.
- Push notification: a webhook fires on completion. Use for hours-long jobs.
- "A2A standardizes communication, not orchestration: delegation, splitting and stopping stay with the harness."

=== Page 42 ===
(footer 45) MCP: agent → capability.
- MCP is the agent ↔ service boundary: one tool call, one result.
- MCP standardizes: tools (callable, typed capabilities); resources (readable data the host may attach); prompts (reusable interaction templates).
- One client speaks to many servers.
- The host, not the model, decides what is exposed.
[Figure: an Agent box connected through an MCP layer to four servers: filesystem, database, GitHub, browser.]

=== Page 43 ===
(footer 47; printed footer 46 is absent from the extraction) MCP vs. A2A. Table — row | MCP | A2A:
- Primary abstraction | capability / tool | agent / task
- Relationship | agent → service | agent → agent
- Discovery | tools, resources, prompts | agent capabilities
- Unit of work | one tool invocation | long-running task
- Internal state | capability interface | ideally opaque
- Analogy | device / API interface | service-to-service RPC
- Key point: "One A2A remote agent may itself call twenty MCP servers."

=== Page 44 ===
(footer 48) Design principles. Four numbered items:
1. Is multi-agent really necessary? Single agent is sufficient; multiple agents often only add overhead and complexity.
2. Decide topology: reflect task dependencies, minimize communication.
3. Identify information-loss points: treat aggregation nodes as places where detail drops.
4. Identify failure-containment boundaries: make sure the system does not stall.
- Closing note: "A dense mesh is rarely the best default. More communication can increase context pressure without increasing useful information."

=== Page 45 ===
(footer 49; last text in the file) Next class.
- Agent design III
- Agent memory
- Agent reliability
- Agent evaluation

=== Page 46 ===
(fetch 無法取得內容) 文字抽取在印刷編號 49（Next class）之後沒有任何內容。這一頁若存在，沒有可抽取的文字；也可能實際只有 45 頁。待開 PDF 核對。
