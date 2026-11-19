<!-- File: docs/pycognition_framework_paper.md -->
<!-- Version: 1.0.0 | Release Date: 2026-11-19 -->

# PyCognition: A Unified Dual-Process Neuro-Symbolic Architecture for Amortized Execution, Self-Healing Skill Refactoring, and Longitudinal Episodic Orchestration

* **Deutsch:** *PyCognition: Eine vereinheitlichte zweistufige neuro-symbolische Architektur für amortisierte Ausführung, selbstheilendes Skill-Refactoring und longitudinale episodische Orchestrierung*
* **Русский:** *PyCognition: Единая двухуровневая нейросимволическая архитектура для амортизированного исполнения, самовосстанавливающегося рефакторинга навыков и продольной эпизодической оркестрации*

**Author:** Oleh Riabtsev  
**Affiliation:** Universität Vechta, Referat Forschung, Nachwuchsförderung und Transfer (RFNT), Vechta, Germany  
**ORCID:** 0009-0003-7848-6418  
**Date:** November 19, 2026  
**Software Repository:** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition) (`v1.3.0`, LGPL-3.0-or-later)  
**Production Reference Implementation:** Grant Harvester v2.2.0 (`DOI: 10.5281/zenodo.24106395`)  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

---

## Abstract

Large Language Model (LLM) agents exhibit strong zero-shot reasoning and code synthesis capabilities, yet their deployment in continuous, long-lived production workflows is constrained by three systemic bottlenecks: (1) prohibitive marginal latency and token expenditure on recurring deterministic operations, (2) structural fragility and database corruption when external web interfaces or schemas drift over time, and (3) stateless snapshot blindness that fragments identical entities across multiple sources and erases longitudinal lifecycle transitions.

In this paper, we present **PyCognition**, an open-source, domain-agnostic neuro-symbolic orchestration framework ([https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)) grounded in Dual-Process Cognitive Theory. PyCognition unifies fast, deterministic procedural execution (**System 1**) with deliberative LLM synthesis, structural reflection, and semantic arbitration (**System 2**) across three tightly integrated architectural layers: (i) **Utility-Guided Just-In-Time (JIT) Skill Compilation**, which crystallizes repetitive algorithmic intents into verified Python subroutines; (ii) **Telemetry-Driven, Capability-Scoped Skill Refactoring**, which replaces record-level *toxic micro-compensation* with Abstract Syntax Tree (AST) audited code repair and monotonic regression gating; and (iii) **Bitemporal Episodic Memory and Multi-Horizon Planning**, which consolidates multilingual and cross-portal entities via crystallized alias caches and tracks lifecycle state transitions (`DEADLINE_EXTENDED`, `STATUS_EXPIRING_SOON`, `STATUS_EXPIRED`, `STATUS_REOPENED`). Across three controlled benchmarks ($N=100$ heterogeneous operational tasks, `WebDrift-Fault-50`, and `ChronoDrift-Entity-60`) and a live 24-portal academic funding observatory (*Grant Harvester*, 1,230 records), PyCognition achieves an **$11,326.7\times$ marginal latency speedup** (`0.292 ms` System 1 execution), a **94.0% reduction in self-healing LLM calls** with **zero database poisoning**, **$F_1 = 1.000$ cross-source entity resolution**, and a **$31.1\times$ wall-clock speedup** (`674.7 s` to `21.7 s`) with **zero recurring System 2 calls** in warm production cycles across 958 consolidated canonical entities.

**Keywords:** Neuro-Symbolic AI, Dual-Process Cognitive Architecture, Autonomous Agents, Self-Healing Software, Skill Crystallization, Bitemporal Event Graphs, Entity Resolution, PyCognition.

---

## 1. Introduction

Autonomous agents powered by Large Language Models have rapidly evolved from single-turn conversational assistants into persistent software systems capable of web navigation, structured data extraction, API orchestration, and institutional knowledge management [1, 2]. However, transitioning an LLM agent from an interactive prototype to a continuously running production service exposes a fundamental architectural mismatch: **frontier neural inference is typically treated as a stateless, per-event runtime engine rather than an amortized compiler and cognitive supervisor.**

In real-world operational environments—such as continuous academic funding intelligence, regulatory compliance monitoring, and Current Research Information System (CRIS) synchronization—this stateless paradigm fails along three distinct dimensions:

1. **Unamortized Computational Cost:** Executing a multi-billion-parameter transformer for every recurring parsing, validation, or transformation step incurs second-scale latency and linear token costs, even when the underlying operation is strictly deterministic.
2. **Brittle Execution and Toxic Micro-Compensation:** When an external portal alters its Document Object Model (DOM) layout or API structure, cached scripts fail. Naively invoking an LLM to patch missing fields record-by-record—a pathology we term *toxic micro-compensation*—causes linear token escalation and poisons downstream databases with hallucinated values or conversational refusal strings.
3. **Temporal and Cross-Source Amnesia:** Persisting each monitoring cycle as an independent snapshot keyed by `(title, URI)` hashes fragments identical entities published in multiple languages (e.g., German and English) or syndicated across portals, while erasing longitudinal state changes such as deadline extensions or seasonal program reopenings.

### 1.1 Purpose and Practical Utility of PyCognition

**PyCognition** ([https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)) is engineered as a lightweight, embeddable Python orchestration layer that converts high-cost LLM reasoning into permanent, auditable symbolic assets. Rather than replacing frontier LLMs or requiring expensive domain-specific fine-tuning, PyCognition provides:

* **Predictable Sub-Millisecond Runtime Performance:** Recurring algorithmic and extraction tasks execute locally in pure Python (`System 1`) with zero network round-trips and zero token cost.
* **Verifiable Security and Structural Self-Healing:** Generated or repaired code is statically audited against declarative capability policies (`ASTSafetyAuditor`) and validated via monotonic quality gates before hot-reloading into production.
* **Longitudinal Entity Intelligence:** A built-in bitemporal graph (`TemporalEventGraph`) and dual-tier entity resolver (`NeuroSymbolicEntityResolver`) deduplicate multilingual records, audit historical attribute deltas, and trigger proactive actions across immediate, tactical, and strategic time horizons.

---

## 2. Related Work

### 2.1 Dual-Process Cognition and Tool-Synthesizing Agents

Kahneman's Dual-Process Theory [3] distinguishes fast, automatic, low-effort processing (**System 1**) from slow, analytical, deliberative reasoning (**System 2**). Recent agent architectures—including ReAct [1], Voyager [2], and LATM [4]—demonstrate that LLMs can synthesize reusable code tools. PyCognition advances this paradigm by formalizing a **utility-theoretic routing arbiter** (`MetaArbiter`), quantitative **runtime degradation telemetry** (`TelemetryEvaluator`), and **capability-scoped AST sandboxing** that prevents self-modifying code from introducing security vulnerabilities or silent data corruption.

### 2.2 Episodic Memory and Neuro-Symbolic Entity Resolution

Long-term agent memory frameworks such as Generative Agents [5], MemGPT [6], and Zep [7] establish the importance of structured historical representations over flat context windows. Bitemporal databases [8] further separate real-world validity time (`valid_time`) from system ingestion time (`transaction_time`). In Entity Resolution (ER), classical probabilistic record linkage [9] and deep cross-encoders [10] are increasingly supplemented by zero-shot LLM matchers [11], which offer high multilingual accuracy at high API cost. PyCognition bridges both worlds: deterministic lexical and institutional acronym anchors handle clear matches and non-matches at zero cost, while System 2 arbitrates only borderline pairs and permanently crystallizes its verdicts in SQLite (`AliasMemoryStore`).

---

## 3. System Architecture

PyCognition (`v1.3.0`) is organized into three cooperative layers inside `src/pycognition/`: the **Dual-Process Execution Core**, the **Telemetry-Driven Skill Refactoring Subsystem** (`pycognition.skills`), and the **Bitemporal Episodic Memory & Horizon Planning Subsystem** (`pycognition.temporal`).

```text
  +-------------------------------------------------------------------+
  |               Incoming Task / External Observation                |
  +---------------------------------+---------------------------------+
                                    |
                                    v
  +-------------------------------------------------------------------+
  | Layer 1: Dual-Process Execution & JIT Compilation                 |
  |   • MetaArbiter: Utility-theoretic routing (System 1 vs System 2) |
  |   • ProceduralRunner (System 1): Sub-ms local Python execution    |
  |   • SkillCrystallizer (System 2): Synthesizes & tests new skills  |
  +---------------------------------+---------------------------------+
                                    |
                                    v
  +-------------------------------------------------------------------+
  | Layer 2: Telemetry-Driven Self-Healing & AST Security             |
  |   • TelemetryEvaluator: Tracks corruption_ratio p_c & yield       |
  |   • ASTSafetyAuditor: Enforces SkillCapability & module allowlist |
  |   • Monotonic Regression Guard: Prevents degraded skill overwrites|
  +---------------------------------+---------------------------------+
                                    |
                                    v
  +-------------------------------------------------------------------+
  | Layer 3: Bitemporal Event Graph & Proactive Orchestration         |
  |   • NeuroSymbolicEntityResolver: Tier-0 Cache + Tier-1 + Tier-2   |
  |   • TemporalEventGraph: Bitemporal EntityNodes & TransitionEdges  |
  |   • ProactiveHorizonPlanner: H1 (0-24h), H2 (1-14d), H3 (14+d)    |
  +-------------------------------------------------------------------+
```

### 3.1 Layer 1: Utility-Guided Dual-Process Execution (`runtime.py`, `arbiter.py`, `memory.py`)

When a task arrives, `VectorStoreMemory` retrieves semantically similar trigger patterns via cosine similarity over TF-weighted representations. `MetaArbiter` evaluates whether to route execution to an existing System 1 routine or invoke System 2 (`LLMDeliberator`) based on expected utility:

$$U(\mathrm{System\;1}) = R_{\mathrm{exec}} - C_{\mathrm{lat}}^{(1)} - P_{\mathrm{fail}} \cdot C_{\mathrm{err}}, \qquad U(\mathrm{System\;2}) = R_{\mathrm{exec}} - C_{\mathrm{tok}}^{(2)} - C_{\mathrm{lat}}^{(2)}$$

For recurring algorithmic or extraction intents where no verified skill exists, System 2 synthesizes a self-contained Python subroutine along with unit assertions, validates it statically and dynamically, and registers it via `SkillRegistry` for zero-downtime hot-reloading on all subsequent invocations.

### 3.2 Layer 2: Telemetry-Driven Refactoring & Capability Sandboxing (`pycognition.skills`)

To survive non-stationary web environments without toxic micro-compensation, `TelemetryEvaluator` inspects the batch output of every System 1 execution and computes a structural corruption ratio:

$$p_c = \frac{N_{\mathrm{corrupt}}}{N_{\mathrm{raw}}}$$

where $N_{\mathrm{corrupt}}$ counts records failing schema invariants, length bounds, or domain refusal-pattern filters. When $p_c > \tau_{\mathrm{crit}}$ (default $0.25$) or yield collapses to zero on a primary entry point, PyCognition triggers **code-level skill refactoring** rather than per-record patching:

1. **Two-Tier Cognitive Reflection:** A fast structural model isolates target DOM/JSON containers from distilled markup, and a reasoning model refactors the `extract(html, base_url)` subroutine.
2. **Capability-Scoped AST Auditing (`SkillCapability` & `ASTSafetyAuditor`):** Before any synthesized code is imported, its AST is inspected against a declarative capability profile (`PARSE_DATA`, `TRANSFORM_TEXT`, `COMPUTE_MATH`), blocking forbidden imports (`os`, `subprocess`, `socket`, `pathlib`), dynamic execution (`eval`, `exec`, `compile`), and dunder attribute traversal (`__subclasses__`, `__globals__`).
3. **Monotonic Regression Guard:** `SkillSandbox` executes the candidate skill against the failing input inside a restricted namespace; the new version is persisted only if its valid record yield strictly exceeds the degraded baseline and its corruption ratio remains below $0.20$.

### 3.3 Layer 3: Bitemporal Event Graph & Entity Resolution (`pycognition.temporal`)

To provide longitudinal awareness across recurring cycles and heterogeneous portals, `pycognition.temporal` processes structured observations through three components:

1. **Dual-Tier Neuro-Symbolic Entity Resolver (`NeuroSymbolicEntityResolver`):** Incoming titles $T_a$ are normalized via Unicode NFKD diacritic folding and stopword filtering into canonical signatures $\sigma(T_a)$.
   * *Tier 0 (`CACHE_HIT`):* Direct $O(1)$ lookup in `AliasMemoryStore` (SQLite) resolves previously crystallized aliases at zero token cost.
   * *Tier 1 (`SYSTEM1_LEXICAL` / `SYSTEM1_DISTINCT`):* Computes hybrid similarity against existing node aliases $T_b$:
     $$S(a, b) = \min\Big(1.0,\; 0.55 \cdot J(W_a, W_b) + 0.45 \cdot \mathrm{Dice}(B_a, B_b) + \beta_{\mathrm{inst}}(a, b) + \beta_{\mathrm{dl}}(a, b)\Big)$$
     incorporating token Jaccard $J$, character bigram $\mathrm{Dice}$, uppercase institutional acronym anchors ($\beta_{\mathrm{inst}} = 0.14$ for shared acronyms $\ge 3$ chars such as `DFG`, `ERC`, `DAAD`, `BMBF`), and ISO-8601 deadline alignment ($\beta_{\mathrm{dl}} = 0.08$). Pairs with $S \ge 0.90$ merge deterministically; pairs with $S < 0.42$ register as distinct entities.
   * *Tier 2 (`SYSTEM2_SEMANTIC`):* Only borderline pairs in the gray zone $0.42 \le S(a, b) < 0.90$ (not already listed in `negative_pairs`) are adjudicated by System 2. Confirmed matches bind $\sigma(T_a) \mapsto \mathrm{id}_{\mathrm{can}}$ in `alias_mappings`; rejected pairs are persisted in `negative_pairs` so distinct instruments from the same agency are never re-queried.
2. **Bitemporal Event Graph (`TemporalEventGraph`):** Separates `valid_time` from `transaction_time`, maintaining consolidated `EntityNode` records across eight lifecycle states (`NEW`, `ACTIVE`, `UPDATED`, `DEADLINE_EXTENDED`, `EXPIRING_SOON`, `EXPIRED`, `REOPENED`, `ARCHIVED`) and emitting immutable `StateTransitionEdge` deltas.
3. **Proactive Multi-Horizon Planner (`ProactiveHorizonPlanner`):** Maps graph transitions into cooldown-deduplicated actions across immediate (`H1_IMMEDIATE`, 0–24 h), tactical (`H2_TACTICAL`, 1–14 d), and strategic (`H3_STRATEGIC`, 14+ d) horizons.

---

## 4. Experimental Evaluation & Production Results

We evaluated PyCognition across three controlled benchmarks isolating each architectural layer, followed by an end-to-end production deployment.

### 4.1 Computational Amortization (`N = 100` Heterogeneous Tasks)

Across 100 operational requests (85 Zipf-distributed algorithmic tasks spanning 12 functional classes plus 15 unstructured Chain-of-Thought deliberations), PyCognition was compared against a pure frontier LLM baseline:

| Performance Metric | Pure Frontier LLM Baseline | PyCognition (Dual-Process) | Empirical Improvement |
| :--- | :---: | :---: | :---: |
| **System 1 Marginal Execution Latency** | 3,307.41 ms | **0.292 ms** (min 0.10 ms) | **11,326.7x speedup** |
| **Per-Skill Amortization Break-Even ($k$)** | N/A | **$k = 4$** (ideal) / **$k = 5$** (effective) | Full payback after 4–5 calls |
| **85 Algorithmic Tasks Total Runtime** | 281.13 s | **155.46 s** (asynchronous) | **1.81x faster (-44.7% wall-clock)** |
| **Cumulative Token Consumption** | 87,061 tokens | **53,978 tokens** | **-38.0% immediate token reduction** |
| **Quartile 4 (Q4) System 1 Coverage** | 0.0% | **71.4%** (15 of 21 tasks) | Sustained procedural consolidation |

### 4.2 Structural Resilience & AST Security (`WebDrift-Fault-50`, 10 Cycles)

On **WebDrift-Fault-50** (`benchmarks/webdrift_fault_50.json`, 50 structural drift scenarios across 5 fault classes over 10 recurring crawl cycles), telemetry-driven refactoring completely eliminated database poisoning while reducing LLM calls by 94.0%:

| Architecture | Precision | Recall | $F_1$ Score | Poisoned DB Records | Total LLM Calls (10 Cycles) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **B1: Static System 1 (No Reflection)** | 0.353 | 0.429 | 0.387 | 55 | 0 |
| **B2: Pure System 2 LLM (Every Page)** | 1.000 | 1.000 | 1.000 | 0 | 500 |
| **B3: Record-Level Micro-Patching** | 0.353 | 0.429 | 0.387 | 55 | 550 |
| **Ours: PyCognition (Telemetry Refactoring)** | **1.000** | **1.000** | **1.000** | **0** | **30** |

Additionally, `ASTSafetyAuditor` intercepted **10/10 (100%)** adversarial code injection traps (`os`, `subprocess`, `socket`, `eval`, `exec`, `open`, and `__subclasses__` gadgets) prior to sandbox execution.

### 4.3 Longitudinal Entity Resolution & Lifecycle Tracking (`ChronoDrift-Entity-60`)

On **ChronoDrift-Entity-60** (`benchmarks/chronodrift_entity_60.json`, 60 multi-source episodes across 6 weekly snapshots = 360 events covering DE/EN translations, URI migrations, deadline extensions, seasonal reopenings, urgent 14-day windows, and hard-negative agency homonyms):

| Architecture | ER Precision | ER Recall | ER $F_1$ | Transition Recall | Action Recall | Total LLM Calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1: Stateless Hash (`title\|url`)** | 1.000 | 0.741 | 0.851 | 0.000 | 0.000 | 0 |
| **B2: Naive Lexical Matching Only** | 1.000 | 0.889 | 0.941 | 0.000 | 0.000 | 0 |
| **B3: Uncached Pairwise LLM ER** | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 54 |
| **Ours: PyCognition (`v1.3.0`)** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **10** |

Crystallizing System 2 equivalence decisions in `AliasMemoryStore` reduced entity resolution LLM invocations by **81.5%** (10 calls vs. 54 uncached calls; 0 calls on recurring snapshots $t_3 \dots t_6$) while achieving **1.000 recall** across all lifecycle transitions and horizon actions.

### 4.4 Live Production Case Study: *Grant Harvester v2.2.0* (24 Portals, 1,230 Records)

To validate end-to-end performance in an operational setting, PyCognition was deployed as the cognitive engine of **Grant Harvester v2.2.0** (`DOI: 10.5281/zenodo.24106395`), an autonomous observatory monitoring 24 German and European research funding portals (including DFG, BMFTR, ERC, EU Funding & Tenders SPA, Alexander von Humboldt Foundation, VolkswagenStiftung, and Konrad-Adenauer-Stiftung):

| Production Metric | Cold Synchronization (Pass 1) | Warm Synchronization (Pass 2) | Net Operational Gain |
| :--- | :---: | :---: | :---: |
| **Raw Funding Records Processed** | 1,230 | 1,230 | Full 24-portal coverage |
| **Consolidated Canonical Entities** | **958** | **958** | **-272 duplicates (-22.1% redundancy)** |
| **System 2 ER LLM Calls (`deepseek-chat`)** | 37 | **0** | **-100.0% recurring LLM cost** |
| **Wall-Clock Synchronization Latency** | 674.7 s | **21.7 s** | **31.1x speedup (-96.8% runtime)** |

During Pass 1, PyCognition automatically synthesized and self-healed portal extraction skills and consolidated bilingual German/English calls (e.g., *«Karl Schmidt-Rottluff Stipendium»* $\leftrightarrow$ *«Karl Schmidt-Rottluff Scholarship»*) as well as cross-portal announcements (*«ERC Proof of Concept»* $\leftrightarrow$ *«Call for proposals for ERC Proof of Concept»*) into 958 unique canonical entities. On Pass 2, warm alias caches and compiled System 1 skills synchronized the entire 1,230-record repository in **21.7 seconds** with **zero System 2 LLM invocations**.

---

## 5. Discussion, Limitations, and Conclusion

### 5.1 Design Principle: Progressive Cognitive Crystallization

The central insight demonstrated by PyCognition is that **neuro-symbolic efficiency arises from progressive crystallization across all operational strata**: algorithmic plans crystallize into deterministic routines, structural repairs crystallize into AST-verified extractors, and semantic identity judgments crystallize into persistent alias stores. Consequently, System 2 is invoked strictly at the frontier of genuine novelty—when encountering an unseen task class, a broken DOM selector, or an ambiguous cross-lingual entity pair.

### 5.2 Current Limitations and Future Directions

1. **Closed-Loop Upstream Crawl Pruning:** While `TemporalEventGraph` consolidates downstream observations, upstream web crawlers may still traverse non-program pages (e.g., institutional staff directories) on broad portals. Feeding `ProactiveHorizonPlanner` signals back into `TelemetryEvaluator` to prune low-value URL subtrees is a direct avenue for further bandwidth savings.
2. **Transitive Multi-Hop Cluster Reconciliation:** Extending `AliasMemoryStore` with periodic connected-component reconciliation will ensure global consistency when multi-hop transitive equivalences ($A \sim B$ and $B \sim C$) interact with pairwise negative constraints.

### 5.3 Conclusion

We presented **PyCognition**, an open-source dual-process neuro-symbolic orchestration framework that unifies JIT procedural compilation, telemetry-driven AST-audited skill refactoring, and bitemporal episodic memory. Validated across three reproducible benchmarks and a live 24-portal production deployment, PyCognition delivers orders-of-magnitude latency speedups, eliminates structural data corruption, and reduces recurring LLM inference costs to zero. The complete source code, benchmarks, and documentation are openly available on GitHub at [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition).

---

## References

[1] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing Reasoning and Acting in Language Models," in *Proc. 11th Int. Conf. Learning Representations (ICLR)*, Kigali, Rwanda, May 2023. Available: [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

[2] G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar, "Voyager: An Open-Ended Embodied Agent with Large Language Models," *Transactions on Machine Learning Research (TMLR)*, 2024. Available: [https://arxiv.org/abs/2305.16291](https://arxiv.org/abs/2305.16291)

[3] D. Kahneman, *Thinking, Fast and Slow*. New York, NY, USA: Farrar, Straus and Giroux, 2011.

[4] T. Cai, X. Wang, T. Ma, X. Chen, and D. Zhou, "Large Language Models as Tool Makers," in *Proc. 12th Int. Conf. Learning Representations (ICLR)*, Vienna, Austria, May 2024. Available: [https://arxiv.org/abs/2305.17126](https://arxiv.org/abs/2305.17126)

[5] J. S. Park, J. O'Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein, "Generative Agents: Interactive Simulacra of Human Behavior," in *Proc. 36th Annual ACM Symp. User Interface Software and Technology (UIST)*, San Francisco, CA, USA, Oct. 2023, Art. no. 2, pp. 1–22. doi: [10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763).

[6] C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, and J. E. Gonzalez, "MemGPT: Towards LLMs as Operating Systems," *arXiv preprint arXiv:2310.08560*, Oct. 2023. Available: [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)

[7] P. Rasmussen, P. Paliychuk, T. Beauvais, J. Ryan, and D. Chalef, "Zep: A Temporal Knowledge Graph Architecture for Agent Memory," *arXiv preprint arXiv:2501.13956*, Jan. 2025. Available: [https://arxiv.org/abs/2501.13956](https://arxiv.org/abs/2501.13956)

[8] R. T. Snodgrass and I. Ahn, "Temporal Databases," *IEEE Computer*, vol. 19, no. 9, pp. 35–42, Sep. 1986. doi: [10.1109/MC.1986.1663327](https://doi.org/10.1109/MC.1986.1663327).

[9] I. P. Fellegi and A. B. Sunter, "A Theory for Record Linkage," *Journal of the American Statistical Association*, vol. 64, no. 328, pp. 1183–1210, Dec. 1969. doi: [10.1080/01621459.1969.10501049](https://doi.org/10.1080/01621459.1969.10501049).

[10] Y. Li, J. Li, Y. Suhara, A. Doan, and W.-C. Tan, "Deep Entity Matching with Pre-Trained Language Models," *Proceedings of the VLDB Endowment*, vol. 14, no. 1, pp. 50–60, Sep. 2020. doi: [10.14778/3421424.3421431](https://doi.org/10.14778/3421424.3421431).

[11] A. Narayan, I. Chami, L. Orr, and C. Ré, "Can Foundation Models Wrangle Your Data?," *Proceedings of the VLDB Endowment*, vol. 16, no. 4, pp. 738–746, Dec. 2022. doi: [10.14778/3574245.3574258](https://doi.org/10.14778/3574245.3574258).

[12] O. Riabtsev, "PyCognition: Dual-Tier Neuro-Symbolic Cognitive Orchestration Framework with Telemetry-Driven Skill Refactoring and Bitemporal Event Graphs (v1.3.0)," *GitHub Software Repository*, Nov. 2026. Available: [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)

[13] O. Riabtsev, "Grant Harvester: Autonomous Academic Funding Monitoring Framework with Cognitive Multi-Tier Reflection," *Zenodo Software Archive*, Nov. 2026. doi: [10.5281/zenodo.24106395](https://doi.org/10.5281/zenodo.24106395).
