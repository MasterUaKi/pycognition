<!-- File: docs/paper_part3_imrad.md -->
<!-- Version: 1.3.0 | Release Date: 2026-11-17 -->

# Temporal Event Graphs and Longitudinal Episodic Memory in Dual-Tier Neuro-Symbolic Agents: Cross-Source Entity Resolution and Proactive Multi-Horizon Orchestration

* **Deutsch:** *Temporale Ereignisgraphen und longitudinale episodische Gedächtnisse in zweistufigen neuro-symbolischen Agenten: Quellenübergreifende Entitätsauflösung und proaktive Multi-Horizont-Orchestrierung*
* **Русский:** *Темпоральные графы событий и продольная эпизодическая память в двухуровневых нейросимволических агентах: кросс-источниковая резолюция сущностей и проактивная многогоризонтная оркестрация*

**Author:** Oleh Riabtsev  
**Affiliation:** Universität Vechta, Referat Forschung, Nachwuchsförderung und Transfer (RFNT), Vechta, Germany  
**ORCID:** 0009-0003-7848-6418  
**Date:** November 17, 2026  
**Framework Version:** PyCognition v1.3.0  
**Related Software Artifact:** Grant Harvester v2.2.0 (`DOI: 10.5281/zenodo.24106395`)  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

---

## Abstract

Dual-tier neuro-symbolic agents achieve high runtime efficiency and structural resilience by pairing deterministic procedural skills (**System 1**) with deliberative Large Language Model reflection (**System 2**). Yet, when operating continuously over recurring observation cycles in open web environments, existing architectures remain **stateless across time and isolated across sources**: each crawl cycle produces an independent snapshot keyed by brittle `(title, URI)` hashes. Consequently, multilingual translations, cross-portal syndications, and URI migrations fragment identical real-world entities into duplicate records, while longitudinal state transitions—such as deadline extensions, call expirations, and seasonal reopenings—go undetected.

In this paper, we introduce **PyCognition v1.3.0**, extending our neuro-symbolic orchestration core with a **Bitemporal Event Graph** (`TemporalEventGraph`), a **Dual-Tier Neuro-Symbolic Entity Resolver** (`NeuroSymbolicEntityResolver`) backed by persistent alias crystallization (`AliasMemoryStore`), and a **Proactive Multi-Horizon Action Planner** (`ProactiveHorizonPlanner`). Borderline candidate pairs falling within a lexical-structural gray zone $[0.42, 0.90)$ are adjudicated once by System 2 and permanently crystallized into positive alias mappings or negative distinct-pair caches, reducing recurring entity resolution inference cost to zero. We evaluate PyCognition v1.3.0 on the newly introduced **ChronoDrift-Entity-60** longitudinal benchmark (60 episodes across 6 temporal snapshots, 360 events) and on a live 1,230-record multi-portal funding repository (*Grant Harvester*). Experimental results demonstrate **1.000 pairwise entity resolution $F_1$**, **1.000 lifecycle transition and action planning recall**, an **81.5% reduction in System 2 resolution calls** on the benchmark (10 vs. 54 calls), and a **31.1x wall-clock speedup** (from 674.7 s to 21.7 s) with **zero System 2 LLM calls** on warm production synchronization cycles across 958 consolidated canonical entities.

**Keywords:** Neuro-Symbolic AI, Bitemporal Event Graphs, Entity Resolution, Episodic Memory, Multi-Horizon Planning, Self-Healing Agents, PyCognition.

---

## 1. Introduction

Autonomous intelligence agents deployed for continuous domain monitoring—such as academic funding intelligence, regulatory tracking, and scholarly repository synchronization—must reason not merely over static pages, but over **evolving real-world entities across time** [1, 2]. In the preceding phases of the **PyCognition** research program, we addressed two foundational bottlenecks of dual-process cognitive architectures [3]:

1. **Computational Amortization (Part I, v1.0.0) [4]:** Compiling repetitive algorithmic intents from System 2 reasoning into sub-millisecond System 1 Python subroutines, achieving $11,326.7\times$ marginal latency speedups.
2. **Structural Resilience (Part II, v1.2.0) [5]:** Replacing data-level *toxic micro-compensation* with telemetry-driven AST-audited skill refactoring (`TelemetryEvaluator`, `SkillCapability`, `SkillCrystallizer`), eliminating database poisoning and reducing LLM calls by 94.0% on the `WebDrift-Fault-50` benchmark.

### 1.1 Limitations of Stateless Snapshot Harvesting

Even with self-healing System 1 skills, agents that persist each crawl cycle via cryptographic hashes of `(title, URI)` suffer from three structural pathologies in longitudinal deployments:

1. **Cross-Source & Cross-Lingual Fragmentation:** German and European funding agencies routinely publish identical calls in German and English under distinct paths (e.g., *«Karl Schmidt-Rottluff Stipendium»* vs. *«Karl Schmidt-Rottluff Scholarship»*) or syndicate programs across both agency websites and the EU Funding & Tenders portal. Hash-based deduplication splits a single real-world entity into multiple unlinked records.
2. **Longitudinal State Blindness:** Overwriting database rows on subsequent cycles erases temporal provenance. When an agency extends an application deadline (`DEADLINE_EXTENDED`), closes a call (`STATUS_EXPIRED`), or reopens a seasonal fellowship cohort (`STATUS_REOPENED`), stateless storage fails to emit structured transition events.
3. **Reactive Execution:** Without explicit temporal state transitions, downstream workflows (e.g., institutional repository ingestion, researcher alerting, or targeted verification re-crawls) must poll raw tables rather than reacting to prioritized horizon triggers.

### 1.2 Contributions

To endow neuro-symbolic agents with longitudinal episodic memory and proactive agency, PyCognition v1.3.0 introduces four contributions:

1. **Bitemporal Event Graph (`TemporalEventGraph`):** A SQLite-backed graph separating real-world validity time (`valid_time`) from ingestion time (`transaction_time`), representing entities as consolidated `EntityNode` instances connected by immutable `StateTransitionEdge` deltas.
2. **Dual-Tier Neuro-Symbolic Entity Resolution (`NeuroSymbolicEntityResolver`):** A hybrid matcher combining token Jaccard, character bigram Dice, and uppercase institutional acronym blocking anchors (`System 1`) with one-time `System 2` semantic arbitration inside a calibrated gray zone $[0.42, 0.90)$, permanently crystallizing decisions in `AliasMemoryStore`.
3. **Proactive Multi-Horizon Planner (`ProactiveHorizonPlanner`):** A policy-driven scheduler mapping graph transitions into deduplicated actions across immediate (`H1`, 0–24 h), tactical (`H2`, 1–14 d), and strategic (`H3`, 14+ d) horizons.
4. **Open Benchmark (`ChronoDrift-Entity-60`) & Production Validation:** Empirical evaluation across 60 longitudinal scenarios and a live 1,230-record repository (*Grant Harvester v2.2.0*).

---

## 2. Related Work

### 2.1 Episodic Memory and Temporal Knowledge Graphs in LLM Agents

Long-term memory architectures for autonomous agents—such as Generative Agents [6], MemGPT [7], and Zep [8]—highlight the necessity of structuring historical observations beyond flat context windows. Temporal Knowledge Graphs (TKGs) formalize evolving facts as quadruples $(s, r, o, t)$ [9], while bitemporal data models [10] distinguish when an event occurred in the external world (`valid_time`) from when the system recorded it (`transaction_time`). PyCognition v1.3.0 adapts bitemporal event modeling specifically for dual-process agents: rather than invoking an LLM to summarize every historical state, deterministic state-transition rules compute field-level deltas in sub-millisecond time while delegating only ambiguous cross-source identity resolution to System 2.

### 2.2 Neuro-Symbolic Entity Resolution

Entity Resolution (ER) traditionally relies on blocking keys followed by pairwise similarity scoring or fine-tuned cross-encoders [11]. Recent LLM-based ER frameworks (e.g., Narayan et al. [12]) achieve high zero-shot accuracy on multilingual and noisy text pairs, but incur $O(N^2)$ or $O(N \cdot B)$ API calls across recurring batch runs. By coupling deterministic blocking anchors (`_extract_acronyms`) with a persistent positive/negative decision cache (`AliasMemoryStore`), PyCognition amortizes System 2 semantic judgments to strictly **one call per novel alias pair** across the entire operational lifetime of the system.

---

## 3. Methodology & Architecture (`pycognition.temporal`)

PyCognition v1.3.0 encapsulates longitudinal memory and planning in `src/pycognition/temporal/` across three cohesive modules: `graph.py`, `resolver.py`, and `planner.py`.

```text
  [Harvested Observation o_t = (title, uri, deadline, attrs)]
                              |
                              v
  +-----------------------------------------------------------+
  | 1. NeuroSymbolicEntityResolver (temporal/resolver.py)     |
  |   • Tier 0: AliasMemoryStore lookup -> CACHE_HIT (0 LLM)  |
  |   • Tier 1: Lexical + Acronym Anchor score s              |
  |       - s >= 0.90 -> SYSTEM1_LEXICAL (0 LLM)              |
  |       - s <  0.42 -> SYSTEM1_DISTINCT (0 LLM)             |
  |   • Tier 2: 0.42 <= s < 0.90 -> System 2 Semantic Arbiter |
  |       - Crystallizes positive alias or negative pair      |
  +---------------------------+-------------------------------+
                              | canonical_id
                              v
  +-----------------------------------------------------------+
  | 2. TemporalEventGraph (temporal/graph.py)                 |
  |   • Bitemporal tracking (valid_time, transaction_time)    |
  |   • Emits StateTransitionEdge: CREATED, ALIAS_MERGED,     |
  |     DEADLINE_EXTENDED, STATUS_EXPIRING_SOON,              |
  |     STATUS_EXPIRED, STATUS_REOPENED                       |
  +---------------------------+-------------------------------+
                              | list[StateTransitionEdge]
                              v
  +-----------------------------------------------------------+
  | 3. ProactiveHorizonPlanner (temporal/planner.py)          |
  |   • H1_IMMEDIATE (0–24h): Urgent deadline/reopen alerts   |
  |   • H2_TACTICAL (1–14d): Metadata consolidation & sync    |
  |   • H3_STRATEGIC (14+d): Archival & institutional export  |
  +-----------------------------------------------------------+
```

### 3.1 Dual-Tier Entity Resolution with Alias Crystallization

Given an incoming observation $o_t$ with title $T_a$, deadline $D_a$, and funding organization $F_a$, `NeuroSymbolicEntityResolver` first normalizes $T_a$ via Unicode NFKD diacritic folding and stopword removal into a canonical signature $\sigma(T_a)$.

1. **Tier 0 — Crystallized Alias Cache (`CACHE_HIT`):** If $\sigma(T_a)$ exists in `AliasMemoryStore`, the cached `canonical_id` is returned immediately in $O(1)$ SQLite lookup time with zero LLM tokens.
2. **Tier 1 — Hybrid Lexical & Institutional Blocking Score:** For uncached titles, System 1 computes similarity against existing node aliases $T_b$:
   $$S(a, b) = \min\Big(1.0,\; 0.55 \cdot J(W_a, W_b) + 0.45 \cdot \text{Dice}(B_a, B_b) + \beta_{\text{inst}}(a, b) + \beta_{\text{dl}}(a, b)\Big)$$
   where $J$ is token Jaccard similarity, $\text{Dice}$ is character bigram similarity, $\beta_{\text{inst}} = 0.14$ if uppercase institutional acronyms ($\ge 3$ chars, e.g., `DFG`, `ERC`, `DAAD`, `BMBF`) or normalized funder names match, and $\beta_{\text{dl}} = 0.08$ if ISO-8601 deadlines align. Pairs with $S \ge 0.90$ merge deterministically (`SYSTEM1_LEXICAL`), while pairs with $S < 0.42$ register as distinct entities (`SYSTEM1_DISTINCT`).
3. **Tier 2 — Gray-Zone System 2 Arbitration (`SYSTEM2_SEMANTIC`):** Only pairs satisfying $0.42 \le S(a, b) < 0.90$ (and not previously recorded in `negative_pairs`) are forwarded to `semantic_arbiter`. Positive matches bind $\sigma(T_a) \mapsto \text{canonical\_id}$ in `alias_mappings`; negative verdicts persist $(\sigma(T_a), \sigma(T_b))$ in `negative_pairs` so distinct tracks from the same agency (e.g., *ERC Starting Grant* vs. *ERC Synergy Grant*) are never re-queried.

### 3.2 Bitemporal Event Graph & Lifecycle State Machine

`TemporalEventGraph` models each consolidated real-world entity as an `EntityNode` occupying one of eight canonical states: `NEW`, `ACTIVE`, `UPDATED`, `DEADLINE_EXTENDED`, `EXPIRING_SOON`, `EXPIRED`, `REOPENED`, or `ARCHIVED`.

Upon ingesting `EntityObservation(canonical_id, source_id, raw_uri, title, attributes, deadline_iso, valid_time, transaction_time)`, the graph evaluates field-level deltas and emits an immutable `StateTransitionEdge`:

* **Reopening (`STATUS_REOPENED`):** Triggered when a node in `EXPIRED` or `ARCHIVED` state is re-observed with a future deadline ($D_{\text{new}} > t_{\text{valid}}$).
* **Deadline Shifts (`DEADLINE_EXTENDED` / `DEADLINE_SHORTENED`):** Triggered when $D_{\text{new}} > D_{\text{old}}$ or $D_{\text{new}} < D_{\text{old}}$.
* **Horizon Thresholds (`STATUS_EXPIRING_SOON` / `STATUS_EXPIRED`):** Triggered either during ingestion or autonomously via `sweep_temporal_horizons(reference_time, expiring_window_days=14)` when $0 \le D - t_{\text{ref}} \le 14\text{ days}$ or $D < t_{\text{ref}}$.
* **Cross-Source Consolidation (`ALIAS_MERGED`):** Triggered when a newly resolved alias or secondary portal URI attaches to an existing canonical node.

### 3.3 Proactive Multi-Horizon Action Planning

`ProactiveHorizonPlanner` maps emitted `StateTransitionEdge` events to `TriggerPolicy` rules partitioned across three temporal horizons:

* **`H1_IMMEDIATE` (Critical/High):** `STATUS_EXPIRING_SOON` $\to$ `DISPATCH_URGENT_ALERT`; `STATUS_REOPENED` $\to$ `DISPATCH_REOPENED_NOTICE`.
* **`H2_TACTICAL` (High/Medium):** `DEADLINE_EXTENDED` $\to$ `UPDATE_DEADLINE_RECORD`; `ALIAS_MERGED` $\to$ `CONSOLIDATE_CROSS_SOURCE_METADATA`; `CREATED` $\to$ `ENRICH_AND_INDEX_ENTITY`.
* **`H3_STRATEGIC` (Low):** `STATUS_EXPIRED` $\to$ `ARCHIVE_EXPIRED_ENTITY`.

Per-entity cooldown windows (`cooldown_hours`) prevent notification storms across frequent polling cycles.

---

## 4. Experimental Evaluation

### 4.1 Controlled Longitudinal Benchmark: `ChronoDrift-Entity-60`

To evaluate longitudinal resolution and lifecycle tracking under reproducible temporal dynamics, we created **ChronoDrift-Entity-60** (`benchmarks/chronodrift_entity_60.json`), comprising **60 multi-source episodes** observed across **6 weekly snapshots** ($t_1 \dots t_6$, **360 total events**) evenly divided into six scenario classes (10 episodes each):

* **Class A (`A_CROSS_LINGUAL_ALIAS`, E01–E10):** Alternating German and English versions of identical DFG, BMBF, and DAAD funding programs.
* **Class B (`B_URI_MIGRATION_SYNDICATION`, E11–E20):** Cross-portal syndication between `erc.europa.eu` and `ec.europa.eu` plus a mid-horizon URL migration at $t_4$.
* **Class C (`C_DEADLINE_SHIFT`, E21–E30):** Sequential deadline extensions at $t_3$ and $t_5$.
* **Class D (`D_EXPIRATION_REOPENING`, E31–E40):** Call expiration at $t_3$ followed by seasonal cohort reopening at $t_5$.
* **Class E (`E_URGENT_HORIZON_SWEEP`, E41–E50):** Entry into the 14-day urgent window at $t_4$ and expiration at $t_6$.
* **Class F (`F_HARD_NEGATIVE_HOMONYMS`, E51–E60):** Distinct funding tracks from the same agency sharing identical acronyms and deadlines (testing false-positive merge resistance).

We compared four architectures across all 360 temporal observations:

1. **B1 (`Stateless_Hash`):** SHA-256 deduplication over `(title, raw_uri)`.
2. **B2 (`Naive_Lexical`):** Deterministic similarity threshold ($\ge 0.90$) without System 2 arbitration or lifecycle tracking.
3. **B3 (`Uncached_LLM_ER`):** Pairwise LLM arbitration on gray-zone candidates without persistent alias caching or horizon planning.
4. **Ours (`PyCognition_v1.3`):** Full `NeuroSymbolicEntityResolver` + `AliasMemoryStore` + `TemporalEventGraph` + `ProactiveHorizonPlanner`.

| Architecture | ER Precision | ER Recall | ER $F_1$ | Transition Recall | Action Recall | Total LLM Calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1: Stateless Hash (`title\|url`)** | 1.000 | 0.741 | 0.851 | 0.000 | 0.000 | 0 |
| **B2: Naive Lexical Only** | 1.000 | 0.889 | 0.941 | 0.000 | 0.000 | 0 |
| **B3: Uncached LLM ER** | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 54 |
| **Ours: PyCognition v1.3.0** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **10** |

**Key Findings:**

* **Perfect Cross-Source Clustering Without False Merges:** PyCognition v1.3.0 achieved **ER Precision = 1.000, ER Recall = 1.000, ER $F_1$ = 1.000**, merging every DE/EN pair (Class A) and migrated URI (Class B) while keeping all 10 hard-negative homonym pairs (Class F) strictly separate.
* **81.5% Amortization of Entity Resolution LLM Calls:** Compared to uncached pairwise LLM arbitration (`B3`, 54 calls), `AliasMemoryStore` reduced System 2 invocations to **10 calls** (strictly 1 call per novel cross-lingual pair in Class A; 0 calls on $t_3 \dots t_6$).
* **100% Lifecycle & Action Recall:** Every deadline extension, expiration, reopening, and urgent horizon entry was captured (`Transition Recall = 1.000`) and mapped to its corresponding horizon action (`Action Recall = 1.000`).

### 4.2 Production Case Study: *Grant Harvester v2.2.0* (1,230 Live Portal Records)

We integrated `pycognition.temporal` into **Grant Harvester v2.2.0** and executed a two-pass synchronization over the live 24-portal SQLite vault (`grants_vault.db`, **1,230 active records**):

| Metric | Cold Synchronization Pass (Run 1) | Warm Synchronization Pass (Run 2) | Improvement / Delta |
| :--- | :---: | :---: | :---: |
| **Raw Vault Records Evaluated** | 1,230 | 1,230 | Full repository coverage |
| **Consolidated Canonical Entities** | **958** | **958** | **-272 duplicates (-22.1% redundancy)** |
| **System 2 ER LLM Calls (`deepseek-chat`)** | 37 | **0** | **-100.0% LLM token expenditure** |
| **Total Wall-Clock Execution Time** | 674.7 s | **21.7 s** | **31.1x speedup (-96.8% latency)** |

During the cold pass, System 2 accurately merged cross-lingual German/English scholarship pairs (e.g., *«Karl Schmidt-Rottluff Stipendium»* $\leftrightarrow$ *«Karl Schmidt-Rottluff Scholarship»*, *«Logo der Stiftung»* $\leftrightarrow$ *«Logo of the Foundation»*) and cross-portal announcements (*«ERC Proof of Concept»* $\leftrightarrow$ *«Call for proposals for ERC Proof of Concept»*), while rejecting hundreds of distinct staff/program titles from the same institutions. On the subsequent warm pass, `AliasMemoryStore` resolved all 1,230 records into the 958 canonical entities in **21.7 seconds** with **zero LLM invocations**.

---

## 5. Discussion, Limitations & Conclusion

### 5.1 Unified Three-Tier Cognitive Amortization

Across Parts I–III of the PyCognition framework, a consistent architectural principle emerges: **System 2 reasoning should never be spent on recurring execution paths, recurring selector failures, or recurring entity comparisons.** By crystallizing algorithmic plans into procedural skills (Part I), selector repairs into AST-audited modules (Part II), and semantic equivalence judgments into bitemporal alias caches (Part III), the marginal inference cost of a continuously operating neuro-symbolic agent converges asymptotically toward zero.

### 5.2 Limitations

1. **Upstream Extraction Noise Propagation:** As observed in our live repository experiment (where institutional staff directory links from one foundation portal entered the raw vault), entity resolution operates downstream of System 1 extraction. Coupling `ProactiveHorizonPlanner` feedback back to `TelemetryEvaluator` to prune noisy sub-paths represents a promising direction for closed-loop crawl refinement.
2. **Transitive Cluster Merging:** While `AliasMemoryStore` caches pairwise equivalence and non-equivalence decisions, large-scale multi-hop alias chains ($A \sim B$ and $B \sim C$) require periodic connected-component reconciliation when conflicting negative constraints arise.

### 5.3 Conclusion

We presented **PyCognition v1.3.0**, completing a three-stage neuro-symbolic architecture capable of learning procedural skills, repairing structural extraction drift, and reasoning longitudinally over evolving cross-source entities. Validated on `ChronoDrift-Entity-60` and in live production monitoring across 24 academic funding portals, bitemporal event graphs coupled with crystallized alias memory eliminate duplicate fragmentation while reducing recurring entity resolution inference cost to zero.

---

## References

[1] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing Reasoning and Acting in Language Models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2023.  
[2] G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar, "Voyager: An Open-Ended Embodied Agent with Large Language Models," *Trans. Machine Learning Research (TMLR)*, 2023.  
[3] D. Kahneman, *Thinking, Fast and Slow*. New York, NY, USA: Farrar, Straus and Giroux, 2011.  
[4] O. Riabtsev, "pycognition: A Dual-Process Cognitive Architecture Integrating Deterministic Procedural Execution and Deliberative LLM Synthesis," *Zenodo Preprint*, Nov. 2026. doi: 10.5281/zenodo.10000000.  
[5] O. Riabtsev, "Telemetry-Driven Skill Refactoring and Capability-Scoped Sandboxing in Dual-Tier Neuro-Symbolic Agents: Preventing Toxic Micro-Compensation in Open Web Environments," *Zenodo Preprint*, Nov. 2026.  
[6] J. S. Park, J. O'Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein, "Generative Agents: Interactive Simulacra of Human Behavior," in *Proc. 36th Annual ACM Symp. User Interface Software and Technology (UIST)*, pp. 1–22, 2023. doi: 10.1145/3586183.3606763.  
[7] C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, and J. E. Gonzalez, "MemGPT: Towards LLMs as Operating Systems," *arXiv preprint arXiv:2310.08560*, 2023.  
[8] P. Rasmussen et al., "Zep: A Temporal Knowledge Graph Architecture for Agent Memory," *arXiv preprint arXiv:2501.13956*, 2025.  
[9] B. Cai, Y. Xiang, L. Gao, H. Zhang, Y. Li, and J. Li, "Temporal Knowledge Graph Completion: A Survey," in *Proc. Int. Joint Conf. Artificial Intelligence (IJCAI)*, pp. 6545–6553, 2023.  
[10] R. T. Snodgrass and I. Ahn, "Temporal Databases," *IEEE Computer*, vol. 19, no. 9, pp. 35–42, 1986.  
[11] Y. Li, J. Li, Y. Suhara, A. Doan, and W.-C. Tan, "Deep Entity Matching with Pre-Trained Language Models," *Proc. VLDB Endowment*, vol. 14, no. 1, pp. 50–60, 2020.  
[12] A. Narayan, I. Chami, L. Orr, and C. Ré, "Can Foundation Models Wrangle Your Data?," *Proc. VLDB Endowment*, vol. 16, no. 4, pp. 738–746, 2022.  
[13] O. Riabtsev, "Grant Harvester: Autonomous Academic Funding Monitoring Framework with Cognitive Multi-Tier Reflection," *Zenodo Software Archive*, Nov. 2026. doi: 10.5281/zenodo.24106395.
