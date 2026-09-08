# Agent coordination references

Sources from the parallel/sequential review and follow-up. Takeaways are practical interpretations within each source's scope, not guarantees for other models or tasks.

## Research

### Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets

[Tran and Kiela, April 2026, revised paper](https://arxiv.org/html/2604.02460v2) · [original version](https://arxiv.org/html/2604.02460v1)

- **Premise:** Compare single-agent and multi-agent reasoning with matched thinking-budget caps on text-only multi-hop question answering.
- **Takeaway:** Do not default to extra reasoning workers. Context isolation can help when context use degrades. Budget caps do not ensure equal actual token use or monetary cost; the results do not establish a coding-specific effort ladder.

### Capable language models can outgrow the benefits of collaboration

[Kim et al., Nature Machine Intelligence, July 2026](https://www.nature.com/articles/s42256-026-01268-y)

- **Premise:** Test coordination structures across 260 configurations and six agentic benchmarks, including software engineering and terminal tasks.
- **Takeaway:** Choose coordination by task dependencies and verify its benefit against a single-agent baseline. Do not turn the observed roughly 45% task-success threshold into a model-score cutoff. The coding evaluations use 20-task subsets with wide uncertainty.

Earlier work: [Towards a Science of Scaling Agent Systems](https://arxiv.org/html/2512.08296v2) and the authors' [Google Research overview](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) cover the earlier 180-configuration study. Use the final publication for its expanded results and limitations.

### Why Do Multi-Agent LLM Systems Fail?

[Cemri et al., MAST, revised October 2025](https://arxiv.org/html/2503.13657v3) · [code and trace resources](https://github.com/multi-agent-systems-failure-taxonomy/MAST)

- **Premise:** Classify failures in 1,642 traces from seven multi-agent frameworks, including design, communication, and verification failures.
- **Takeaway:** Define ownership, preserve decision context, and verify required behavior rather than superficial completion. Targeted interventions improved results but did not resolve all failures. The reported failure range describes the tested systems, not a general failure rate for subagents.

### AI Agents That Matter

[Kapoor et al., July 2024 preprint](https://arxiv.org/html/2407.01502v1)

- **Premise:** Evaluate agent accuracy alongside cost, simple baselines, and benchmark reproducibility.
- **Takeaway:** Include retries and coordination in the comparison with simpler approaches. In its HumanEval comparison, LATS cost about 55 times the warming baseline and had lower mean accuracy; this is not a universal cost multiplier.

### Self-Manager: Parallel Agent Loop for Long-form Deep Research

[Xu et al., January 2026](https://arxiv.org/html/2601.17879v1)

- **Premise:** Run asynchronous research subthreads with isolated contexts and compare information retention, research quality, and cost with sequential agent loops.
- **Takeaway:** Isolate large investigations when context interference is a problem, and return focused results. Better retention came with higher overhead; this is evidence from deep research, not proof of cheaper repository work.

### Optimizing Sequential Multi-Step Tasks with Parallel LLM Agents

[Zhang et al., M1-Parallel, July 2025](https://arxiv.org/html/2507.08944v1)

- **Premise:** Run multiple agent teams on alternative solution paths, using early termination or result aggregation.
- **Takeaway:** Separate latency gains from cost savings. Deliberate diversity prompting added no benefit over repeated sampling in these experiments. Alternative attempts can help particular setups, but should not become a default escalation rule.

## Engineering experience

### Building effective agents

[Anthropic](https://www.anthropic.com/engineering/building-effective-agents)

- **Premise:** Describe simple workflow patterns, autonomous agents, and when added orchestration is useful.
- **Takeaway:** Use the simplest adequate execution path. Deterministic operations need not become reasoning assignments; evaluator loops earn their cost only when evaluation can distinguish an acceptable result. These principles do not determine our model assignments.

### Codex best practices

[OpenAI](https://developers.openai.com/codex/learn/best-practices)

- **Premise:** Give coding agents focused context, explicit constraints, and concrete ways to verify their work.
- **Takeaway:** Define acceptance before dispatch, preserve required behavior, and report checks actually performed. Assess passing checks against the requirement rather than treating them as proof by themselves. Keep detailed evidence accessible without repeatedly copying the conversation.

### Codex subagents

[OpenAI](https://developers.openai.com/codex/multi-agent)

- **Premise:** Describe native delegation and model/effort configuration for spawned workers.
- **Takeaway:** A role label does not establish the worker's effective model or effort. Set supported controls explicitly and verify the selection when exposed by the runtime. Resolve configuration uncertainty when it matters, without adding a full configuration audit to every task.

### How we built our multi-agent research system

[Anthropic, June 2025](https://www.anthropic.com/engineering/multi-agent-research-system)

- **Premise:** Describe an orchestrator-worker system for broad research, with independent searches and centralized synthesis.
- **Takeaway:** Give workers distinct questions, clear boundaries, and evidence-backed outputs. Delegate when additional coverage justifies the overhead. The 15-times token comparison is against ordinary chat, not a matched single-agent coding run.

### How and when to build multi-agent systems

[Harrison Chase, LangChain, June 2025](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems)

- **Premise:** Compare the context and coordination demands of read-heavy and write-heavy workflows.
- **Takeaway:** Parallelize independent retrieval more readily than state-changing work. Agree shared decisions before parallel writes; separate files alone do not prevent incompatible outcomes. The article does not prohibit all parallel writing.

### Don't Build Multi-Agents

[Walden Yan, Cognition, June 2025](https://cognition.com/blog/dont-build-multi-agents)

- **Premise:** Explain how missing context and conflicting implicit decisions undermine delegated work.
- **Takeaway:** Preserve relevant decisions and their rationale, and keep dependent implementation together. Use source artifacts when a short handoff omits necessary evidence; copying every trace is not a default requirement for this skill.

### Don't Sleep on Single-agent Systems

[Graham Neubig, OpenHands, September 2024](https://www.openhands.dev/blog/dont-sleep-on-single-agent-systems)

- **Premise:** Examine the context loss and rigidity of splitting software development into specialized agents.
- **Takeaway:** Avoid a mandatory chain of specialist handoffs. Keep enough source access and tools with the active worker to finish and check its assignment.

## Discussion credit

[u/PilgrimofHaqq2: Parallel vs Sequential Agent Systems](https://www.reddit.com/r/claude/comments/1w7k9au/parallel_vs_sequential_agent_systems_research/)

- **Premise:** Collect research and engineering arguments about parallel and sequential agent workflows.
- **Takeaway:** A useful reading list; verify quantitative claims and broad rules against the primary sources above. Dependency structure is a better dispatch criterion than a blanket read/write distinction.

The [README credits](../README.md#credits) retain the project's earlier model-routing and polling references. Model-cost data remains in the [benchmark workbook](benchmarks/GPT-model-efficiency-2026-09-08.xlsx).
