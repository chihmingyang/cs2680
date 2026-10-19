# L07 slides 逐頁筆記

- 來源：https://cs2680.com/slides/7_agent_design_4.pdf
- 頁數：36（PDF 檢視器的頁數，封面 = 1）
- 整理：2026-10-19，WebFetch 逐頁整理；內容是 paraphrase，不是原文
- 用途：寫文章時取事實與頁碼。承接、演進的句子要以這裡為依據。
- 頁碼校正：WebFetch 把 slide 右下角的 footer 號碼當頁碼，footer 會跳號（隱藏的 slide）。本檔已換算成 PDF 頁數。 跳過的 footer 號碼：[34]。
  footer → PDF：35–37 → 34–36
- 頁數疑問：兩次 WebFetch（逐頁與頁面清單）都得到 36 頁，footer 跳過 35；docs/l07.html 的 data-pages-total 寫 37，文章引用的 p.34、p.35 與這份筆記一致。請在 PDF 檢視器確認總頁數。

=== Page 1 ===
Title: "Modern AI systems: agents and system optimizations." Presenter: Juncheng Yang. Lecture: "Agent design IV: evaluation." Course site: course.agentic-system.org (Harvard MaDSys).

=== Page 2 ===
Title: Logistics.
- Office hour this Thursday, 3:30pm, SEC 4.308.
- Final project poster presentation: 9am-1pm, Dec 7.
- If that time doesn't work, reach out before the end of this week.
- Assignment 2 is due this Sunday; start early.

=== Page 3 ===
Title: Logistics: Claude Code session log.
- Package everything related. Missing parts of the full session log incur a penalty on Assignment 2.
- Log location: ~/.claude/projects/ (macOS/Linux) or C:\Users\<YourUsername>\.claude\projects\ (Windows).
- Uploading more is fine.
- AI use is not penalized, but some parts of the assignment must be your own work.
- Survey of 17 students who used Claude on the writeup: 6 used it to polish writing; a few had it turn bullet points into prose; 7 wrote a draft and edited it (discouraged); a few pasted from other sources (ChatGPT?). 4 had near-verbatim Claude output; 2 left Claude Code TODOs in the writeup.
- A short reflection write-up is required.
- Do NOT manipulate session logs; that is an academic integrity violation. Three students tried to erase history.
- AI-generated writing is easy to detect, and hiding history is harder than doing the assignment.

=== Page 4 ===
Title: Plan for today.
- Agent evaluation.
- Cost-effective agents.

=== Page 5 ===
Title: How do you evaluate an agent's capability?
- Outline: history and trends, metrics, representative benchmarks, challenges.

=== Page 6 ===
Title: Different ways to evaluate an agent.
- Two-by-two framing: component-level (inside the agent) vs. end-to-end.
- Component-level items: planning (task decomposition); tool use (discovery, selection, parameterization); memory (extraction, consolidation, retrieval); error recovery.
- End-to-end items: success rate (did the task get done?); cost (spend per task); latency (time to finish).

=== Page 7 ===
Title: A bit of history.
Timeline of benchmarks by era:
- Before 2018, language modeling and narrow tasks: Penn Treebank, WikiText, LAMBADA, SQuAD.
- 2018–2019, transfer learning and general NLU: GLUE, SuperGLUE, ARC, HellaSwag, WinoGrande.
- 2020–2022, foundation-model capability: MMLU, BIG-bench, GSM8K, MATH, HumanEval, TruthfulQA, HELM.
- 2023–2024, agents, tool use, context, modalities: MT-Bench, Chatbot Arena, AlpacaEval, IFEval, LongBench, MMMU, GPQA, AgentBench, WebArena, GAIA, SWE-bench, OSWorld, τ-bench.
- 2024–2025, difficulty, robustness, freshness: MMLU-Pro, LiveBench, LiveCodeBench, MMMU-Pro, FrontierMath, Humanity's Last Exam.
- 2025–2026, larger scope, less specific instructions, realistic use cases, new problems: GDPval, BrowseComp, Terminal-Bench, ARC-AGI-3.
- Source: cs2680.com agent-evaluation notes.

=== Page 8 ===
Title: Evaluation objectives (table). Columns: objective, representative benchmarks, what success means.
- Predict text | PTB, WikiText | assign high probability to observed text.
- Produce a correct answer | MMLU, GSM8K, GPQA, HLE | match a known answer.
- Produce a preferred response | Arena, AlpacaEval, MT-Bench | favorable human or model judgments.
- Produce functioning code | HumanEval, LiveCodeBench, SWE-bench | pass executable tests.
- Complete an interactive task | WebArena, OSWorld, τ-bench, Terminal-Bench | reach the required environment state.

=== Page 9 ===
Title: Evaluation objectives (same table repeated, identical to page 8).
- Predict text (PTB, WikiText); correct answer (MMLU, GSM8K, GPQA, HLE); preferred response (Arena, AlpacaEval, MT-Bench); functioning code (HumanEval, LiveCodeBench, SWE-bench); interactive task (WebArena, OSWorld, τ-bench, Terminal-Bench).

=== Page 10 ===
Title: Metrics.
- Earlier benchmarks: perplexity (exponentiated average negative log-likelihood on held-out text; lower is better); accuracy or F1; preference or win rate.
- Capability: pass@k (at least one of k solutions passes); pass^k (all k pass; introduced by τ-bench).
- Cost: mostly LLM cost. Overlooked items include tool calls and other costs (e.g., LLM cache misses).
- Latency/duration: not just LLM time.

=== Page 11 ===
Title: Benchmark evaluation loop.
- Pseudocode: for each task, reset the environment to its initial state. While not terminated and within budget: observe, let the agent choose an action from (task instruction, observation, history, tools), execute it.
- After the loop, a task evaluator scores the final answer, final environment state, and trajectory.

=== Page 12 ===
Title: GAIA: General AI Assistant.
- 466 human-written questions covering web browsing, spreadsheets, PDFs, images, audio, and calculation.
- Answers are short: a number, string, or list (e.g., 17.4 or 4,381).
- No fixed tool API; each agent brings its own search, browser, Python, and shell.
- Tests the whole agent system, not just the LLM.
- Difficulty levels: Level 1 (≤5 steps, zero or one tool); Level 2 (5–10 steps, multiple tools); Level 3 (arbitrarily long, many tools).
- Source: Mialon et al., GAIA, arXiv 2023.

=== Page 13 ===
Title: GAIA: can an assistant research and return the right answer?
- Example task: a spreadsheet lists films. Find the film meeting two conditions, look up its director, and report the director's birthplace.
- Agent steps shown: search, open webpage, download PDF, extract table, run Python, answer 4,381. The answer was discarded by the evaluator.
- Scoring: only the final answer counts; exact match after normalization, averaged over N questions.
- Measures reasoning, retrieval, tool selection, and synthesis with clean grading.
- Does not measure actions such as sending email, booking a flight, modifying a database, submitting a form, or updating an issue.

=== Page 14 ===
Title: BFCL: is the model's tool interface reliable?
- Example prompt: "Book the cheapest flight from Boston to Chicago next Monday."
- Available tools: search_flights(...), book_flight(flight_id, passenger_id), get_weather(...).
- Correct behavior: search, pick the cheapest, then book.
- Failure modes: inventing a passenger ID (should ask the user); an irrelevant get_weather call.
- Scoring: AST or execution checks. Multi-turn checks state and the reply at every turn.
- V4 adds web search and memory. Read category scores, not the composite.
- Source: Patil et al., Berkeley Function Calling Leaderboard, ICML 2025.

=== Page 15 ===
Title: WebArena: can the agent complete a web workflow?
- Example: in GitLab, create the issue "Update onboarding documentation," assign it to Alex, and add the documentation label.
- Loop: observe the accessibility tree; act with click, type, or stop.
- Scoring: reset snapshot, trajectory, final state, functional checks, success 1/0.
- 812 tasks on self-hosted shopping, admin, Reddit, GitLab, maps, and Wikipedia sites.
- Issue tasks check that the issue exists with the right assignee and label. Other tasks check the final URL, page content, backend state, or text answer.
- WebArena-Verified (ServiceNow, 2025): structured output and deterministic checks on HTTP traces, removing LLM-as-judge.
- Sources: Zhou et al., WebArena, ICLR 2024; WebArena-Verified, 2025.
- [Figure: flow diagram of accessibility-tree observations and click/type actions, then the scoring pipeline from reset snapshot to success 1/0.]

=== Page 16 ===
Title: OSWorld: can the agent operate an actual computer?
- Example: add a computed column, sort, and save as result.xlsx.
- Observations are screenshots (pixels); actions are mouse and keyboard.
- Scoring: setup logic, trajectory, final state, evaluator f, reward R. Some setup steps are not scored.
- 369 tasks across browser, office, file, and system apps.
- Cross-application workflows, spreadsheet cells and formulas, and checks on settings, files, and app config.
- OSWorld 2.0 (2026): 108 long workflows (often 1+ hour), hundreds of steps, about 27 checkpoints for partial credit.
- Source: Xie et al., OSWorld, NeurIPS 2024.
- [Figure: screenshot-and-action sequence (click LibreOffice, click cell, type formula, save file) feeding into the evaluator pipeline.]

=== Page 17 ===
Title: SWE-bench: can the agent fix a real repository issue?
- Typical loop: grep the repo, inspect the implementation and tests, run tests, modify a file, run tests again, debug, produce a patch.
- Scoring: apply the agent's patch, run the tests, mark resolved or not. Human-verified subset.
- Variants: Lite (300-task subset), Multilingual (9 languages), Multimodal (image issues), Pro (harder, multi-file).
- Example: a library function raises an exception on an empty index. Make it return an empty result while preserving existing behavior.
- Sources: Jimenez et al., 2024; OpenAI, 2024; Deng et al., 2025; swebench.com.

=== Page 18 ===
Title: τ-bench: can an agent interact with a user, obey policy, and change backend state?
- Two interacting actors: a simulated user (an LLM playing a customer) and an agent bound by airline policy, plus tools and an airline database where API calls change real state.
- Policy example: basic economy tickets cannot be modified.
- Example task: "I need to change my flight tomorrow to the evening flight."
- Typical flow: verify identity, look up reservation, search flights, explain fare difference, get confirmation, call change_booking, reservation updated.
- Scoring: evaluate the final database state.
- Source: Yao et al., τ-bench, arXiv 2024.

=== Page 19 ===
Title: τ-bench scores end state and consistency.
- Reward: r = r_action × r_output.
- r_action = 1 only if the final database matches the annotated goal state. Read-only calls may vary, but unintended writes cause failure.
- r_output = 1 only if the user-facing response includes the required information.
- pass^k: probability that all k independent runs of the same scenario succeed. Pass@k needs only one success; pass^k is deliberately stricter.
- Example: 4 of 4 runs succeed for pass^k.
- The τ³-bench implementation adds corrected tasks, more domains, knowledge retrieval, and voice evaluation.
- Source: Yao et al., τ-bench, arXiv 2024.

=== Page 20 ===
Title: Terminal-Bench: can an agent finish a real task through a shell?
- Task domains: programming, sysadmin and server config, data processing, model training, security, scientific workflows. End-to-end work, not only repo bug fixes.
- Packaging: task instruction (instruction.md), Dockerfile, agent shell trajectory, final system state, test suite (tests/test.sh), pass or fail.
- Counts: 89 tasks in TB 2.0, reduced to 66 in TB 4.0 (saturated tasks pruned). Hidden human solutions; 8-hour timeout.
- Representative task: deploy a new protocol on a live KV service with no dropped connections and held latency.

=== Page 21 ===
Title: Terminal-Bench sits between SWE-bench and OSWorld (comparison table).
- Actions: SWE-bench edits files in one repo; Terminal-Bench runs shell commands in a container; OSWorld uses mouse clicks and keystrokes.
- Observations: code and test output; terminal output; screenshots.
- Scope: fix one GitHub issue; configure, debug, repair, and build; operate any desktop app.
- Scoring: repo tests; tests on final system state; checks on final state.
- Terminal-Bench tests long-horizon reasoning and system interaction without mouse-coordinate prediction.
- Source: Merrill et al., Terminal-Bench 2.0, arXiv 2026.

=== Page 22 ===
Title: TheAgentCompany: mimicking a company.
- Simulated company with GitLab (code), Plane (tickets), ownCloud (documents), RocketChat (team chat), and LLM-simulated coworkers.
- Example end-to-end job: read ticket in Plane, ask a coworker in RocketChat, inspect repo in GitLab, write code in workspace, run tests in terminal, update the issue in Plane, report the result in RocketChat.
- 175 tasks spanning software, project management, data science, HR, and finance.
- Partial credit via checkpoints. Formula: S_partial = 0.5 × (earned/total) + 0.5 × S_full.
- Score examples: 4/8 checkpoints, incomplete = 0.25; 7/8, incomplete = 0.44; 8/8, complete = 1.00.
- Source: Xu et al., TheAgentCompany, arXiv 2024.

=== Page 23 ===
Title: Agent benchmarks (summary table). Columns: benchmark, agent operates in, typical actions, what is graded.
- GAIA | web/files/code tools | search, inspect files, calculate | short final answer.
- WebArena | self-hosted websites | click, type, navigate | website or backend state.
- OSWorld | full desktop VM | mouse, keyboard, app interaction | files, app state, system state.
- SWE-bench | software repository | inspect, edit, run tests | patch passes tests.
- BFCL | function/API interface | structured function calls | calls, arguments, resulting state.
- τ-bench | customer-service APIs and dialogue | talk to user, call APIs | database state and response.
- Terminal-Bench | isolated terminal container | arbitrary shell commands | task-specific verifier tests.
- TheAgentCompany | simulated software company | web apps, code, files, coworkers | workflow checkpoints and final system state.

=== Page 24 ===
Title: Section divider: "Agent Evaluation is Challenging and Evolving."
- Sections: Challenges; Evolution.

=== Page 25 ===
Title: Data leakage: four layers, not just training.
- Training leakage: the task or its human fix was in the training data.
- Eval-time leakage: the agent web-searches and copies the future fix.
- Environment leakage: the sandbox exposes future commits or hidden tests.
- Benchmark overfitting: prompts and scaffold are tuned on the public test set.
- Trade-off: realistic tools enlarge the leakage surface; required benchmark info may be searchable.

=== Page 26 ===
Title: Leakage can occur through the whole agent stack.
- Performance formula: P = f(LLM, prompt, scaffold, tools, retriever, memory, environment).
- Leakage table (component: possible leakage):
  - Base model: benchmark examples in pretraining.
  - Fine-tuning: benchmark solutions used as agent-training trajectories.
  - Prompt: few-shot examples derived from test tasks.
  - Retrieval: benchmark answers indexed in a RAG corpus.
  - Memory: previous benchmark attempts stored.
  - Web search: published task solutions retrieved.
  - Environment: future Git commits or hidden artifacts exposed.
  - Scaffold: hand-coded heuristics tuned to the benchmark.
  - Agent development: researchers repeatedly inspect test failures and tune the system.
- Takeaway: saying "the model was not trained on the test set" is not sufficient.

=== Page 27 ===
Title: Challenges with agent evaluation: a single user turn.
- Most benchmarks give one fully specified instruction: prompt in, final state out, no user in the loop.
- Real work is ambiguous, revised, and interrupted: missing constraints, mid-task corrections, shifting goals.
- Single-turn scoring rewards confident guessing. Asking a clarifying question costs steps and earns no credit.

=== Page 28 ===
Title: Challenges with agent evaluation: a single user turn (continued).
- Slide text: "This is how you used Claude Code in Assignment 1."
- [Figure: screenshot-style image of the student's Claude Code usage from Assignment 1; no extractable text.]

=== Page 29 ===
Title: Challenges with agent evaluation: a single user turn (title only).
- No additional text.
- [Figure: image-only slide, no extractable text.]

=== Page 30 ===
Title: Challenges with agent evaluation: a single user turn (with evaluation dimensions).
- Repeats the single-turn bullets from page 27.
- Three dimensions for multi-turn evaluation:
  - Clarification: does the agent ask when the goal is underspecified?
  - Recovery: does it re-plan after a mid-task correction?
  - Memory: does it carry constraints across turns?

=== Page 31 ===
Title: Challenges with agent evaluation: there are more.
- Cost and latency: success rate alone is not enough. Example: a 200-step, $40 run vs. a 12-step, $0.30 run.
- Non-determinism: the same agent on the same task can produce different outcomes, so single-run scores are noise, not signal.
- Safety and side effects: nothing penalizes deleted files, sent emails, or money spent on the way to a pass.
- Metrics: outcome-only scoring passes lucky or unsafe runs; trajectory matching fails valid ones.
- Call for help: the MaDSys group is building a research platform for agent evaluation using real traffic. Contact the instructor if interested and able to commit 20+ hours per week.

=== Page 32 ===
Title: How fast the frontier caught up.
Six charts, each showing model score over 0–4 years (y-axis 0–100):
- GLUE (2018): human level (87.1) reached in 14 months; top score 91.1.
- MMLU (2020): expert level (89.8) reached in 39 months; top score 92.3.
- GPQA Diamond (2023): PhD experts (69.7) reached in 10 months; top score 96.0.
- SWE-bench Verified (2024): 33% → 95% in 22 months; top score 95.0.
- ARC-AGI-2 (2025): average human (60) reached in 11 months; top score 95.0.
- ARC-AGI-3 (2026): 0.5% → 62.7% in 6 months (marked with an asterisk); top score 62.7.
- [Figure: six small line charts, one per benchmark, with era labels across the bottom.]

=== Page 33 ===
Title: Benchmarks saturate quickly.
- Timeline grid (2016 to Sep 2026) plotting benchmarks by category: narrow tasks (SQuAD 1.1); NLU suites (GLUE, SuperGLUE); knowledge and reasoning (ARC-AGI-1, MMLU, MATH, HumanEval, GPQA Diamond, MMMU, FrontierMath, Humanity's Last Exam, ARC-AGI-2); assistants (Chatbot Arena, MT-Bench); agents (WebArena, SWE-bench → Verified, OSWorld, Terminal-Bench, GDPval, SWE-bench Pro, Remote Labor Index, ARC-AGI-3, OSWorld 2.0).
- Saturated = frontier reached the human baseline or top models stopped separating. Still open items are marked separately.
- [Figure: timeline chart with colored category bands and saturation status per benchmark.]

=== Page 34 ===
Title: Agent evaluation is still evolving (comparison table). Columns: dimension, earlier evaluation, current frontier.
- Objective evaluated | base model | model + prompt + tools + agent harness.
- Interaction | static, single-turn | stateful and long-horizon.
- Grader | exact match or likelihood | tests, environment state, humans, or judge models.
- Dataset | fixed and public | fresh, hidden, dynamic, or contamination-aware.
- Main metric | average accuracy | system efficiency alongside task success, reliability, quality, cost, and latency.
- Primary concern | generalization across examples | robust completion under realistic constraints and safety requirements.

=== Page 35 ===
Title: More dimensions to consider for a real-world agent.
- Four axes: capability, cost, speed, agent usability.
- Assignment 3 will be graded on three metrics: capability (higher is better), cost (lower is better), and one more (speed is not drawn on the chart).
- Pareto dominance: A dominates B if A is no worse on any metric and better on at least one.
- Rank 1 is the Pareto frontier. Rank 2 and Rank 3 are dominated points.
- [Figure: scatter plot with capability on the y-axis and cost on the x-axis; points labeled Rank 1, Rank 2, Rank 3; "Better" direction indicated.]

=== Page 36 ===
Title: Next class.
- Cost-effective agents.
- Case study.
- Different types of agents.
- Agentic frameworks.

TOTAL PAGES: 36
