<!-- File: README.md -->
<!-- Version: 1.3.1 | Release Date: 2026-11-17 -->

# pycognition

[![Version: 1.3.0](https://img.shields.io/badge/Version-1.3.0-blue.svg)](https://github.com/MasterUaKi/pycognition/releases/tag/v1.3.0)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0003--7848--6418-green.svg)](https://orcid.org/0009-0003-7848-6418)
[![Case Study DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24106395.svg)](https://doi.org/10.5281/zenodo.24106395)
[![Benchmarks](https://img.shields.io/badge/Benchmarks-N100%20%7C%20WebDrift--50%20%7C%20ChronoDrift--60-informational.svg)](benchmarks/)

> **A Dual-Process Neuro-Symbolic Cognitive Architecture Integrating Deterministic Procedural Execution, Telemetry-Driven Skill Refactoring, and Bitemporal Episodic Memory**

`pycognition` is an open-source neuro-symbolic orchestration framework formalizing Daniel Kahneman's **Dual-Process Cognitive Theory** for autonomous software agents. Across three architectural generations (`v1.0.0` $\to$ `v1.2.0` $\to$ `v1.3.0`), the framework systematically eliminates recurring LLM inference costs across execution, self-healing, and longitudinal memory:

1. **Part I (`v1.0.0`) — Computational Amortization (JIT Skill Compilation):** Compiles repetitive algorithmic intents from deliberative **System 2** reasoning into sub-millisecond **System 1** Python subroutines (`0.292 ms` mean latency, `11,326.7x` marginal speedup).
2. **Part II (`v1.2.0`) — Structural Resilience (Telemetry-Driven Skill Refactoring):** Replaces data-level *toxic micro-compensation* in non-stationary web environments with quantitative `corruption_ratio` telemetry, declarative `SkillCapability` AST auditing, and monotonic regression guards (`94.0%` LLM call reduction and `0` database poisoning on `WebDrift-Fault-50`).
3. **Part III (`v1.3.0`) — Longitudinal Agency (Bitemporal Event Graphs & Cross-Source Entity Resolution):** Replaces stateless `(title, URI)` snapshots with a bitemporal state-transition graph (`TemporalEventGraph`), dual-tier cross-lingual entity resolution with persistent alias crystallization (`NeuroSymbolicEntityResolver`, `AliasMemoryStore`), and proactive multi-horizon action planning (`ProactiveHorizonPlanner`).

---

## Table of Contents

- [Unified Three-Tier Architecture](#unified-three-tier-architecture)
- [Part I: JIT Compilation & Amortized Inference (N = 100)](#part-i-jit-compilation--amortized-inference-n--100)
- [Part II: Telemetry-Driven Skill Refactoring & AST Sandboxing (WebDrift-Fault-50)](#part-ii-telemetry-driven-skill-refactoring--ast-sandboxing-webdrift-fault-50)
- [Part III: Bitemporal Event Graphs & Entity Resolution (ChronoDrift-Entity-60)](#part-iii-bitemporal-event-graphs--entity-resolution-chronodrift-entity-60)
- [Live Production Validation: Grant Harvester v2.2.0](#live-production-validation-grant-harvester-v220)
- [Installation & Configuration](#installation--configuration)
- [Quickstart](#quickstart)
- [Repository Structure](#repository-structure)
- [Scientific Manuscripts & Citation](#scientific-manuscripts--citation)
- [License & Author](#license--author)

---

## Unified Three-Tier Architecture

```text
                       +-----------------------------------+
                       |   Incoming Task / Observation     |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------------------------+
                       |     MetaArbiter & System 1        |
                       |  • ProceduralRunner (~0.292 ms)   |
                       |  • Token Cost: 0 tokens           |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------------------------+
                       |   TelemetryEvaluator (v1.2.0)     |
                       |  • Computes corruption_ratio p_c  |
                       +--------+-----------------+--------+
                                |                 |
                 p_c <= 0.25    |                 | p_c > 0.25 (DEGRADED)
                (Healthy Yield) |                 v
                                |   +-------------------------------+
                                |   | System 2 Reflection & AST Guard|
                                |   | • Tier 1/2 Code Refactoring   |
                                |   | • SkillCapability AST Audit   |
                                |   | • Monotonic Regression Guard  |
                                |   +---------------+---------------+
                                |                   | Hot-Reload
                                +-------------------+
                                         |
                                         v
                       +-----------------------------------+
                       | NeuroSymbolicEntityResolver(v1.3) |
                       |  • Tier 0: AliasMemoryStore Cache |
                       |  • Tier 1: Lexical + Acronym Score|
                       |  • Tier 2: Gray-Zone [0.42, 0.90) |
                       +-----------------+-----------------+
                                         | canonical_id
                                         v
                       +-----------------------------------+
                       |    TemporalEventGraph (v1.3.0)    |
                       |  • Bitemporal State Transitions   |
                       |  • ProactiveHorizonPlanner (H1-H3)|
                       +-----------------------------------+
```

---

## Part I: JIT Compilation & Amortized Inference (`N = 100`)

Evaluated across **100 heterogeneous operational requests** (85 Zipf-distributed algorithmic tasks across 12 functional classes + 15 unstructured Chain-of-Thought deliberations):

| Performance Dimension | Pure Frontier LLM Baseline | `pycognition` (Dual-Process) | Empirical Delta / Gain |
| :--- | :---: | :---: | :---: |
| **System 1 Marginal Latency** | 3,307.41 ms (algo) | **0.292 ms** (min 0.10 ms) | **11,326.7x faster** (sub-millisecond) |
| **Script Synthesis & Testing Latency** | 0 ms (no synthesis) | **7,192.20 ms** (mean) | JIT compilation investment |
| **Per-Skill Break-Even Point ($k$)** | N/A | **$k = 4$** (ideal) / **$k = 5$** (effective) | Fully amortized after 4–5 calls |
| **85 Algorithmic Tasks Execution Time** | 281.13 s | **155.46 s** (asynchronous) | **1.81x speedup** (-44.7% execution time) |
| **System Break-Even Horizon ($N^*$)** | N/A | **$N^* \approx 207$ tasks** | Full synchronous cluster payback |
| **Cumulative Token Expenditure** | 87,061 tokens | **53,978 tokens** | **-38.0% immediate token reduction** |
| **Quartile 4 System 1 Coverage (Q4)** | 0.0% | **71.4%** (15 of 21 algorithmic) | Sustained procedural consolidation |

---

## Part II: Telemetry-Driven Skill Refactoring & AST Sandboxing (`WebDrift-Fault-50`)

When deployed in non-stationary web environments, patching missing fields per phantom DOM container via System 2 causes **toxic micro-compensation** (linear token escalation and database poisoning with LLM refusal strings). `pycognition v1.2.0` elevates feedback to AST-audited, sandbox-verified code refactoring (`pycognition.skills`).

Evaluated on **WebDrift-Fault-50** (`benchmarks/webdrift_fault_50.json`, 50 fault cases across 5 classes over a **10-cycle horizon**):

| Architecture | Precision | Recall | $F_1$ Score | DB Poison Count | Total LLM Calls (10 Cycles) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **B1: Static System 1** (No Reflection) | 0.353 | 0.429 | 0.387 | 55 | 0 |
| **B2: Pure LLM (System 2)** (Every Page) | 1.000 | 1.000 | 1.000 | 0 | 500 |
| **B3: Data-Level Micro-Patch** (Per-Record LLM) | 0.353 | 0.429 | 0.387 | 55 | 550 |
| **Ours: `pycognition v1.2.0`** (Telemetry Refactoring) | **1.000** | **1.000** | **1.000** | **0** | **30** |

* **94.0%–94.5% LLM Call Reduction:** Once degraded skills are refactored on Cycle 1, Cycles 2–10 execute at zero marginal LLM cost.
* **100% Adversarial Trap Interception (`10/10`):** `ASTSafetyAuditor` blocked all injected `os`, `subprocess`, `socket`, `eval`, `exec`, `open`, and `__subclasses__` payloads prior to execution.

---

## Part III: Bitemporal Event Graphs & Entity Resolution (`ChronoDrift-Entity-60`)

In `v1.3.0`, `pycognition.temporal` adds longitudinal episodic memory (`TemporalEventGraph`), dual-tier cross-lingual/cross-portal entity resolution with persistent alias crystallization (`NeuroSymbolicEntityResolver`, `AliasMemoryStore`), and proactive multi-horizon planning (`ProactiveHorizonPlanner` across `H1_IMMEDIATE`, `H2_TACTICAL`, and `H3_STRATEGIC`).

Evaluated on **ChronoDrift-Entity-60** (`benchmarks/chronodrift_entity_60.json`, **60 multi-source episodes $\times$ 6 weekly snapshots = 360 events** across 6 scenario classes including DE/EN aliases, URI migrations, deadline extensions, seasonal reopenings, urgent 14-day horizons, and hard-negative institutional homonyms):

| Architecture | ER Precision | ER Recall | ER $F_1$ | Transition Recall | Action Recall | Total LLM Calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1: Stateless Hash (`title\|url`)** | 1.000 | 0.741 | 0.851 | 0.000 | 0.000 | 0 |
| **B2: Naive Lexical Only** | 1.000 | 0.889 | 0.941 | 0.000 | 0.000 | 0 |
| **B3: Uncached LLM ER** | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 54 |
| **Ours: `pycognition v1.3.0`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **10** |

* **81.5% Amortization of Entity Resolution LLM Calls:** Gray-zone pairs $[0.42, 0.90)$ are adjudicated once by System 2 and permanently crystallized in `AliasMemoryStore` (10 calls vs. 54 uncached calls; 0 calls on recurring snapshots).
* **100% Lifecycle & Action Planning Recall:** Detects every deadline shift, expiration, reopening, and urgent horizon threshold.

---

## Live Production Validation: *Grant Harvester v2.2.0*

Integrated into **Grant Harvester v2.2.0** ([DOI: 10.5281/zenodo.24106395](https://doi.org/10.5281/zenodo.24106395)) monitoring 24 German and European academic funding portals (DFG, BMFTR, EU Funding & Tenders SPA, ERC, Alexander von Humboldt Foundation, VolkswagenStiftung, Konrad-Adenauer-Stiftung):

| Synchronization Pass | Raw Vault Records | Consolidated Canonical Entities | System 2 ER LLM Calls | Wall-Clock Time |
| :--- | :---: | :---: | :---: | :---: |
| **Pass 1 (Cold Alias Crystallization)** | 1,230 | **958** (-22.1% duplicates) | 37 | 674.7 s |
| **Pass 2 (Warm Crystallized Memory)** | 1,230 | **958** | **0** (-100.0%) | **21.7 s** (**31.1x faster**) |

---

## Installation & Configuration

```bash
git clone [https://github.com/MasterUaKi/pycognition.git](https://github.com/MasterUaKi/pycognition.git)
cd pycognition

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -e ".[dev]"
```

Environment variables (`.env`):

```bash
DEEPSEEK_API_KEY="your-api-key-here"
DEEPSEEK_BASE_URL="[https://api.deepseek.com/v1](https://api.deepseek.com/v1)"
PYCOGNITION_MODEL="deepseek-chat"
PYCOGNITION_REASONER_MODEL="deepseek-reasoner"
PYCOGNITION_ARBITER_THRESHOLD="0.55"
PYCOGNITION_SKILLS_DIR="./skills_registry"
PYCOGNITION_SANDBOX_TIMEOUT="15.0"
```

---

## Quickstart

### 1. Bitemporal Event Graph, Cross-Source Entity Resolution & Horizon Planning (`v1.3.0`)

```python
import asyncio
from datetime import datetime, timezone
from pycognition.temporal import (
    EntityObservation,
    NeuroSymbolicEntityResolver,
    ProactiveHorizonPlanner,
    TemporalEventGraph,
)

async def main():
    graph = TemporalEventGraph(":memory:")
    resolver = NeuroSymbolicEntityResolver(semantic_arbiter=lambda a, b: True)
    planner = ProactiveHorizonPlanner()

    # Observation 1 (German portal)
    d1 = await resolver.resolve_async(
        "DFG Forschungsstipendien", "dfg_de", "[https://dfg.de/1](https://dfg.de/1)", [], deadline_iso="2026-12-01"
    )
    e1 = graph.ingest_observation(
        EntityObservation(
            canonical_id=d1.canonical_id,
            source_id="dfg_de",
            raw_uri="[https://dfg.de/1](https://dfg.de/1)",
            title="DFG Forschungsstipendien",
            deadline_iso="2026-12-01",
            valid_time=datetime(2026, 11, 1, tzinfo=timezone.utc),
        )
    )

    # Observation 2 (English portal with extended deadline -> triggers System 2 once & crystallizes alias)
    d2 = await resolver.resolve_async(
        "DFG Research Fellowships", "dfg_en", "[https://dfg.de/en/1](https://dfg.de/en/1)", graph.list_nodes(), deadline_iso="2026-12-20"
    )
    e2 = graph.ingest_observation(
        EntityObservation(
            canonical_id=d2.canonical_id,
            source_id="dfg_en",
            raw_uri="[https://dfg.de/en/1](https://dfg.de/en/1)",
            title="DFG Research Fellowships",
            deadline_iso="2026-12-20",
            valid_time=datetime(2026, 11, 8, tzinfo=timezone.utc),
        )
    )

    actions = planner.plan_from_transitions([e1, e2], graph=graph)
    print(f"Track: {d2.track_used.value} | Transition: {e2.transition.value}")
    print(f"Planned Actions: {[a.action_type for a in actions]}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Reproducing All Benchmarks

```bash
# Part II: WebDrift-Fault-50
python benchmarks/generate_webdrift_50.py && python benchmarks/run_benchmark.py

# Part III: ChronoDrift-Entity-60
python benchmarks/generate_chronodrift_60.py && python benchmarks/run_temporal_benchmark.py
```

---

## Repository Structure

```text
pycognition/
├── pyproject.toml                      # PEP 621 build specification (v1.3.0)
├── CITATION.cff                        # Citation File Format metadata (v1.3.0)
├── README.md                           # Canonical documentation
├── LICENSE                             # GNU Lesser General Public License v3.0
├── src/
│   └── pycognition/
│       ├── __init__.py
│       ├── runtime.py                  # DualProcessRuntime: JIT orchestration engine
│       ├── arbiter.py                  # MetaArbiter: utility-theoretic routing
│       ├── memory.py                   # VectorStoreMemory: TF-vector indexing
│       ├── procedural.py               # ProceduralRunner: System 1 execution tier
│       ├── deliberator.py              # LLMDeliberator: System 2 reasoning tier
│       ├── crystallizer.py             # SkillCrystallizer: JIT code & test synthesis
│       ├── validator.py                # ASTSecurityValidator: static AST security
│       ├── registry.py                 # SkillRegistry: zero-downtime hot-reloading
│       ├── schemas.py                  # Pydantic v2 data models and contracts
│       ├── skills/                     # Part II: Telemetry-driven skill refactoring (v1.2.0)
│       │   ├── __init__.py
│       │   ├── capability.py           # ExecutionScope, SkillCapability & ASTSafetyAuditor
│       │   ├── telemetry.py            # TelemetryEvaluator & SkillExecutionTelemetry
│       │   └── crystallizer.py         # SkillSandbox & regression-guarded SkillCrystallizer
│       └── temporal/                   # Part III: Bitemporal event graph & ER (v1.3.0)
│           ├── __init__.py
│           ├── graph.py                # TemporalEventGraph, EntityNode & StateTransitionEdge
│           ├── resolver.py             # NeuroSymbolicEntityResolver & AliasMemoryStore
│           └── planner.py              # ProactiveHorizonPlanner & TriggerPolicy
├── benchmarks/
│   ├── generate_webdrift_50.py         # Part II benchmark generator (50 fault cases)
│   ├── run_benchmark.py                # Part II 4-architecture evaluation runner
│   ├── webdrift_fault_50.json          # Part II open benchmark dataset
│   ├── generate_chronodrift_60.py      # Part III benchmark generator (60 longitudinal episodes)
│   ├── run_temporal_benchmark.py       # Part III 4-architecture evaluation runner
│   └── chronodrift_entity_60.json      # Part III open longitudinal dataset
├── docs/
│   ├── paper_part2_imrad.md            # Part II IMRaD manuscript
│   └── paper_part3_imrad.md            # Part III IMRaD manuscript
└── skills_registry/                    # Storage registry for crystallized Python routines
```

---

## Scientific Manuscripts & Citation

### Software Framework Citation (`PyCognition v1.3.0`)
```bibtex
@software{riabtsev2026pycognition,
  author       = {Riabtsev, Oleh},
  title        = {PyCognition: Dual-Tier Neuro-Symbolic Cognitive Orchestration Framework with Telemetry-Driven Skill Refactoring and Bitemporal Event Graphs},
  version      = {1.3.0},
  year         = {2026},
  month        = {11},
  publisher    = {GitHub},
  url          = {[https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)}
}
```

### Part II Manuscript: Telemetry-Driven Skill Refactoring & Capability-Scoped Sandboxing
```bibtex
@unpublished{riabtsev2026pycognition_part2,
  author       = {Riabtsev, Oleh},
  title        = {Telemetry-Driven Skill Refactoring and Capability-Scoped Sandboxing in Dual-Tier Neuro-Symbolic Agents: Preventing Toxic Micro-Compensation in Open Web Environments},
  note         = {Preprint manuscript, Universit{\"a}t Vechta, Referat Forschung, Nachwuchsf{\"o}rderung und Transfer (RFNT)},
  year         = {2026},
  month        = {11},
  url          = {[https://github.com/MasterUaKi/pycognition/blob/main/docs/paper_part2_imrad.md](https://github.com/MasterUaKi/pycognition/blob/main/docs/paper_part2_imrad.md)}
}
```

### Part III Manuscript: Temporal Event Graphs & Longitudinal Episodic Memory
```bibtex
@unpublished{riabtsev2026pycognition_part3,
  author       = {Riabtsev, Oleh},
  title        = {Temporal Event Graphs and Longitudinal Episodic Memory in Dual-Tier Neuro-Symbolic Agents: Cross-Source Entity Resolution and Proactive Multi-Horizon Orchestration},
  note         = {Preprint manuscript, Universit{\"a}t Vechta, Referat Forschung, Nachwuchsf{\"o}rderung und Transfer (RFNT)},
  year         = {2026},
  month        = {11},
  url          = {[https://github.com/MasterUaKi/pycognition/blob/main/docs/paper_part3_imrad.md](https://github.com/MasterUaKi/pycognition/blob/main/docs/paper_part3_imrad.md)}
}
```

---

## License & Author

This software is released under the **GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)**. See the [LICENSE](LICENSE) file for complete details.

* **Author:** Oleh Riabtsev
* **Affiliation:** Referat Forschung, Nachwuchsförderung und Transfer (RFNT), Universität Vechta, Germany
* **ORCID:** [0009-0003-7848-6418](https://orcid.org/0009-0003-7848-6418)
* **Repository:** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)
