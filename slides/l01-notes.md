# L01 slides 逐頁筆記

- 來源：https://cs2680.com/slides/1_intro.pdf
- 頁數：50（PDF 檢視器的頁數，封面 = 1）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。
- 頁碼對照：slide 右下角的 footer 編號不等於頁數。封面沒有 footer；footer 2、3 = 第 2、3 頁；footer 4 不存在（沒有這一頁）；footer 5 起，頁數 = footer − 1（例：footer 42「What are we optimizing?」= p.41）。下面每頁標題後面的「(footer N)」是 slide 上印的編號，引用時一律用 Page N。

=== Page 1 ===
Cover (no footer). Title: "Modern AI Systems: Agents and System Optimizations". Presenter: Juncheng Yang. Lecture subtitle: "Overview". Course website: https://cs2680.com.

=== Page 2 ===
(footer 2) Plan for today. Three items:
- Course overview
- Policy and logistics
- AI systems and agentic systems

=== Page 3 ===
(footer 3) About me. Juncheng Yang.
- Assistant Professor at SEAS (Harvard)
- Graduated from CMU in 2024
- Previously at AWS, Snowflake, Cloudflare, Twitter
[Figure: likely a portrait photo; not recoverable from text.]

=== Page 4 ===
(footer 5) Harvard MaDSys (Measurement and Design of Computer Systems) Group.
- Four goals, each with two sub-goals:
  - Efficiency: less resources, higher utilization
  - Reliability: less downtime, more robust
  - Performance: faster, more scalable
  - Sustainability: less carbon emission
- Research areas listed around the goals: Storage Systems; Agent Serving Systems; Caching; Sustainable storage; Context management; LLM serving optimizations.
- Motto at the bottom: "People find solutions, we find problems; we measure, design, and operate real systems".
[Figure: cluster/quadrant diagram with the four goals (Efficiency, Reliability, Performance, Sustainability) and the research-area labels placed around the group name.]

=== Page 5 ===
(footer 6) Me and TFs. Course staff: Juncheng Yang (instructor), Yiyu Liu (TF), Yunjia Zheng (TF). Each: "Office hour: by appointment". Course staff email: cs2680-staff@g.harvard.edu.
[Figure: three staff photos side by side; not recoverable from text.]

=== Page 6 ===
(footer 7) Untitled logistics slide. Two lines:
- "I will try to remember everyone's name"
- "Please say your name first before asking or answering questions"

=== Page 7 ===
(footer 8) Next, Your Turn.
- Each table selects a leader to introduce everyone at the table.
- Introduce yourself (5 min): name and where you are from; program, year and background; research interest; why you take this class and what you hope to learn.

=== Page 8 ===
(footer 9) Section divider: "The course". Subtitle: "What you will learn, the assignments, and the project".

=== Page 9 ===
(footer 10) What is this course about.
- "Agentic AI Systems": a graduate-level computer systems course.
- Expected background: one graduate-level systems course (OS, networking, databases, architecture); experience with real systems.
- Two topic areas: agent design; LLM / agent serving systems.

=== Page 10 ===
(footer 11) What you will learn in this course.
- Foundations (first few classes): introduction to LLMs and agents; how to use Claude Code; how to design a coding agent; how to optimize your coding agent.
- Systems for LLMs & agents (majority of classes): GPU programming and kernels; batching, scheduling, memory management; load balancing and routing; KV-cache and prefix-cache; agent serving systems and other optimizations.

=== Page 11 ===
(footer 12) Five assignments (1–3). Three columns (the column grouping of sub-bullets is inferred from layout):
- Assignment 1: Build a web UI for Claude Code. Solve a set of simple problems; create new problems for the assignment 3 leaderboard. Goal: "Experience the magic of coding agents".
- Assignment 2: Build a simple coding agent. Goal: "Understand the lifecycle of coding agent".
- Assignment 3: Optimize your coding agent. Open-ended: context, memory, test-time scaling, routing, subagents, tool call. Metrics: accuracy, cost, latency.

=== Page 12 ===
(footer 13) Five assignments (4–5).
- Assignment 4: Serve your agent. "The hardest assignment, with harder tasks". From a commercial API to a small model.
- Assignment 5: Optimize the full stack. Open-ended: quantization, routing, finetuning, engine–agent co-design. Co-tune your agent and the serving engine for performance.
- Assignments 3 & 5 are scored on the leaderboard: leaderboard ranking + baseline improvement.
- Warnings: "Expect 10+ hours every week"; "Do NOT take this class if you care about GPA".

=== Page 13 ===
(footer 14) Project. Two options:
1. Build a tool: "Find a gap and build a tool you will actually use".
2. Research: "A research project — talk to the TFs first".
- Open-ended, individual project + AI.
- Poster and demo session during reading period.
- Grading: code + report + poster / demo peer review.

=== Page 14 ===
(footer 15) A lot of learning happens after class.
- "Learn the skills to learn"; the course provides pointers.
- Hands-on class: learn by doing the assignments.
- Class time is limited.

=== Page 15 ===
(footer 16) Section divider: "Grading, policy and logistics". Subtitle: "The parts worth reading carefully".

=== Page 16 ===
(footer 17) Grading.
- Five assignments 70%: assignments 1, 2, 4 at 10% each; 3, 5 at 20% each.
- Project 16%.
- Presentation 10%: "paper + assignment 1".
- Participation 4%.
- Bonus 10%: "course feedback + problems that AI cannot solve".
- Late policy: 4 late days throughout the semester; 20% penalty per day for late submission.
- "Assignment 3 and 5 sharing sessions are based on leaderboard ranking".
- Alert: "20% A grading policy enforced · an A or even A- is hard to earn".

=== Page 17 ===
(footer 18) Enrollment.
- Planned and budgeted: 40.
- Enrolled today: 80 (the cap was raised to 80).
- Prospective + cross-registration + waitlist: 68 + 10 + 6.
- Auditing: only if Harvard policy permits and a seat is available.
- Computing resources may not scale with enrollment: you may not get a GPU on the assignment due date.

=== Page 18 ===
(footer 19) Policy: using AI in this course.
- Read the assignment submission page on the course website.
- Disclosure is required: describe what AI helped with and what did not work.
- Upload your session log with every assignment.
- AI use is encouraged, but you must reason about / understand AI-generated code, and you are responsible for all code you submit.

=== Page 19 ===
(footer 20) Policy: attendance and laptops.
- In-person attendance is expected; attendance is required.
- No video recording; the class is not recorded.
- Laptops are allowed; if you keep one open, sit at the back.
- Guest lectures: meeting sign-up opens one week in advance.
- See the website for the full policy.

=== Page 20 ===
(footer 21) Other logistics: computing. "Read the computing page on the website". Four resources:
- Claude Code API access. The slide also shows a standalone, unlabeled line "api.cs2680.com" (most likely the API endpoint; the slide does not say).
- GitHub: private repo, shared with staff.
- Class HPC: everyone with Canvas access is already on the system; SLURM-based; RTX 6000 PRO Blackwell GPUs; course work only.
- AWS: sign up and fill in the Google Form before Friday; terminate or turn off your instance when not in use.
[Figure: resource list, possibly with service logos; text only.]

=== Page 21 ===
(footer 22) Schedule may change during the semester.
- "The first time offering this course: expect a bumpy ride ahead!"
- Grading may change as well ("paper reading").
- Timeline runs from Week 1 to Week 14.
[Figure: horizontal week timeline with endpoints "Week 1" and "Week 14".]

=== Page 22 ===
(footer 23) Section divider: "A few questions first". Subtitle: "To help me understand everyone's background". Introduces the next three polling questions.

=== Page 23 ===
(footer 24) Poll: How many computer systems courses have you taken? Options: operating systems; distributed systems; databases; computer networking; computer architecture; anything else.

=== Page 24 ===
(footer 25) Poll: How many of these topics are you familiar with? Six topics:
- Transformer architecture
- TP / PP / DP / EP parallelism
- Iteration-level scheduling and PagedAttention
- Linear attention
- GPU programming
- Linux kernel

=== Page 25 ===
(footer 26) Poll: How have you used AI? Three levels:
1. Chat
2. Coding agent (MCP, Skills / Plugins, subagents, parallel agents)
3. Customized agent

=== Page 26 ===
(footer 27) Agentic Coding Levels. Scale 0–5:
- 0 No AI: hand-written code.
- 1 Assist: AI autocompletion.
- 2 Supervised: AI writes functions, you review them.
- 3 Scoped: you hand off a task, then review the code.
- 4 Goal-driven: AI writes everything; tests verify.
- 5 Parallel agents: sub-agents split the work.
[Figure: ordinal ladder from level 0 to level 5.]

=== Page 27 ===
(footer 28) Section divider: "Part I — AI Systems". Subtitle: "How they differ from traditional computer systems".

=== Page 28 ===
(footer 29) What is an AI System?
- Many moving parts: scheduling and orchestration, state management, communication, caching, fault tolerance, security, observability.
- Footnote: "AI systems" is a broad term; this course focuses narrowly on LLM systems.
- Two-column contrast:
  - AI / ML asks: "What model should we use?" "How should I design the model?" It picks a model and writes a Python script to solve a task. It optimizes accuracy and capability.
  - AI Systems asks: "How do we train and serve it at scale?" Goals: maximum GPU utilization (performance), minimal resource waste (efficiency), minimal downtime (reliability), lower carbon footprint (sustainability).
[Figure: two-column comparison, AI/ML vs AI Systems.]

=== Page 29 ===
(footer 30) Why should you care about AI systems?
- This is where capability becomes product, and it is harder than the AI itself.
- AI systems are critical digital infrastructure.
- Three benefits: understand model design; design better products; more job opportunities.

=== Page 30 ===
(footer 31) How AI systems differ: compute.
- Heterogeneous computation: CPUs do tokenization, kernel launches, data movement, tool calls; GPUs do matmul. Mixed GPU generations and xPUs are common.
- Distinct phases: prefill is compute-bound; decode is memory-bandwidth-bound. The same deployment can hit a compute, bandwidth, or capacity bottleneck.
- Unpredictable execution time: it depends on output length, which complicates scheduling.

=== Page 31 ===
(footer 32) How AI systems differ: non-deterministic compute.
- Distributivity can fail in floating point: a × (b + c) ≠ a × b + a × c (slide notes this one is "not used widely").
- Transitivity can fail: a == b and b == c do not guarantee a == c.
- Why: floating-point addition is not associative; rounding happens at every operation. "Butterfly effect": a shift in the 7th decimal of a matmul can change the next token.
- Sources of non-determinism:
  - Runtime: warp / block scheduling, memory ordering, async streams, batch size.
  - Software: fused multiply-add vs two separate ops, autotuning, subnormals.
  - Hardware: CUDA cores vs tensor cores; Hopper FP8 vs Blackwell micro-scaling tiles.
- Takeaway: approximate computing is acceptable.

=== Page 32 ===
(footer 33) How AI systems differ: memory, storage and communication.
- Huge state: model weights GBs to TBs; KV-cache 10s to 100s of KB per token; prefix cache = KV reuse across requests. "Data movement is the bottleneck."
- Multi-GPU communication: parallelism types pipeline / tensor / expert / context; collectives NCCL, UCCL; topology NVLink, Ethernet / InfiniBand; CPU and kernel bypass via RDMA.

=== Page 33 ===
(footer 34) How AI systems differ: fast-moving models and workloads.
- Rapidly evolving model architectures: MHA, GQA, MLA, NSA, linear attention, and more.
- Rapidly evolving workloads: multi-turn chat (interactive, latency-sensitive); problem solving (reasoning, long output); RAG (retrieve documents first, long context); agents (long context, prefix caching critical, routing and load balancing).
- Bottom banner principle: adapt the model to the hardware, and design hardware for the model architecture.

=== Page 34 ===
(footer 35) How AI systems differ: reliability, power and energy.
- Reliability: 9% annual failure rate (AFR); 50,000-hour MTBF; in a 16K-GPU cluster one GPU fails about every 3 hours.
- Power and energy: CPU 100–300 W; GPU 700–1000 W; 4–8 GPUs per server; server power rises from 800 W to 6,000 W (8x). Challenge: how to avoid power fluctuation.

=== Page 35 ===
(footer 36) Section divider: "Part II — Agentic AI Systems". Subtitle: "What an agent is, and why it is a systems problem".

=== Page 36 ===
(footer 37) What is an AI agent?
- Definition (on slide): "An AI agent is an autonomous software system that uses an AI model to reason about a goal, use external tools, and execute multi-step actions until a task is finished". No citation on the slide.
- Five-step loop: Plan (break the task into sub-steps); Act (call external tools such as APIs, databases); Observe (interpret the results); Adapt (revise the plan with new information); Deliver (return the final result).
[Figure: loop diagram. Box "Agent" contains "LLM" with "Reasoning & Planning" and "Memory". Agent sends "Action" to "Environment"; Environment returns "Observation" to Agent.]

=== Page 37 ===
(footer 38) Why do we need an AI agent?
- "LLMs are strange computers: superhuman and incompetent at the same time".
- Superhuman at: recalling vast factual knowledge; language; pattern matching; generating code; operating across many domains.
- Surprisingly weak at: persistent memory; reliably understanding context; avoiding hallucinations; knowing what they don't know; security and adversarial input.
- Reference link: https://www.youtube.com/watch?v=LCEmiRjPEtQ&t=874 (Andrej Karpathy, "Software Is Changing (Again)", starting at 874 s). No speaker name printed on the slide.

=== Page 38 ===
(footer 39) Agents as a new kind of computer.
- An LLM is more than a smarter CPU: it is a new kind of programmable computer with a different programming model and a different failure model.
- Mapping (traditional computer → agent): CPU → LLM; RAM / working memory → context window; peripherals → tools; OS → agent harness; application → agent.
[Figure: two side-by-side stacks with arrows: CPU, RAM / working memory, Peripherals, OS, Application on one side; LLM, Context window, Tools, Agent Harness, Agent on the other.]

=== Page 39 ===
(footer 40) Why are agents a systems problem?
- Many turns: the critical path spans GPU, CPU, storage, network, and external services.
- Traditional LLM serving: request → inference → response.
- Agent serving: infer → tool → infer → tool → retrieval → infer → ...
- Challenges: dependencies between steps; highly variable step latency; blocking / waiting on tools; rapidly growing state; concurrency and speculation; failures anywhere in the trajectory.
[Figure: top row is a short linear request → inference → response flow; bottom row is a long chain alternating infer and tool steps, with a retrieval step and trailing "...".]

=== Page 40 ===
(footer 41) The agentic systems stack. Six layers, top to bottom:
- Application / User
- Agent / Harness: planning · context · memory · tools · subagents
- Model
- Serving System: batching · scheduling · routing · caching
- Runtime / Kernels: CUDA · Triton · collectives
- Hardware: GPU · CPU · memory · network · storage
Side elements: "External Environment" with Tools (web · files · APIs · humans) next to the harness layer; "Agent Serving" spanning the serving layers; "Systems" (scheduling · caching); "Hardware co-design" arrow linking agent serving and hardware.
[Figure: vertical layered stack with the six layers, a side box for tools / external environment, and cross-layer arrows labelled Agent Serving, Systems, Hardware co-design.]

=== Page 41 ===
(footer 42) What are we optimizing?
- Key message: "Throughput is the wrong objective for an agent".
- Objective: maximize task success, subject to latency, cost, resources, reliability, and security.
- Two columns:
  - Useful but insufficient: TTFT / TPOT; tool-call latency; GPU utilization.
  - What we actually optimize: task success / accuracy; end-to-end latency; tokens per task; $ per successful task; energy per successful task.
- Caveat: "More tokens/sec can still mean a slower, costlier agent".
[Figure: two-column table, "useful but insufficient" vs "what matters".]

=== Page 42 ===
(footer 43) Agentic systems introduce new systems problems. Each workload property maps to a course topic:
- Long trajectories → state and context management
- Repeated prefixes → prefix caching
- Tool dependencies → dependency-aware scheduling
- Variable tool latency → asynchronous execution
- Multiple agents → orchestration and communication
- Huge context → memory hierarchy and retrieval
- Branching reasoning → speculative execution
- Different models → routing
- External side effects → security and isolation
- Long-running tasks → checkpointing and fault tolerance

=== Page 43 ===
(footer 44) Observability is a first-class problem.
- For agents, the distributed trace becomes a nested trajectory.
- Callout: "You cannot optimize what you cannot observe".
[Figure: nested span tree: Session → Turn → Agent step → (Model request, Tool call, Tool result) → Agent step → Subagent → ...]

=== Page 44 ===
(footer 45) Questions you will think about in this course. Nine questions:
1. Why does batching improve throughput but hurt agent latency?
2. When should an agent use a larger model?
3. Where should KV and prefix state live?
4. How should requests from the same agent be scheduled?
5. Can tool calls overlap with inference?
6. When should we spawn a subagent?
7. How do we route across heterogeneous GPUs and models?
8. How do we recover a 30-minute agent when something fails?
9. How do we optimize dollars per successful task rather than tokens per second?
- By the end of CS2680 you should be able to answer these quantitatively.

=== Page 45 ===
(footer 46) What we will not cover in this course.
- Training (inference dominates compute demand): data pipeline; checkpointing; pre-training, fine-tuning, post-training, RL rollout.
- Cluster management.
- Model architecture design.
- Other inference-related topics: communication; power and energy; new hardware design.

=== Page 46 ===
(footer 47) Next class: LLM basics.

=== Page 47 ===
(footer 48) Blank slide: footer only, no title or body text.

=== Page 48 ===
(footer 49) Section divider: "Optional reading". Title only.

=== Page 49 ===
(footer 50) AI agents vs. AI assistants vs. bots. Comparison table (columns: AI agent | AI assistant | Bot):
- Purpose: autonomously and proactively performs tasks | assists users with tasks | automates simple tasks or conversations
- Capabilities: complex, multi-step actions; learns and adapts; decides independently | responds to prompts; can recommend actions, but the user decides | follows pre-defined rules; limited learning; basic interactions
- Interaction: proactive; goal-oriented | reactive; responds to user requests | reactive; responds to triggers or commands
- Source: https://cloud.google.com/discover/what-are-ai-agents

=== Page 50 ===
(footer 51) Key differences: autonomy, complexity, learning.
- Autonomy: agents operate and decide independently to reach a goal; assistants need user input and direction; bots follow preprogrammed rules.
- Complexity: agents handle complex tasks and multi-step workflows; assistants and bots suit simpler tasks and interactions.
- Learning: agents use machine learning to adapt over time; assistants may learn somewhat; bots learn little or not at all.
- Same source as the previous page (Google Cloud, "What are AI agents").
