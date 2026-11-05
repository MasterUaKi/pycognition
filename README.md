<!-- Version: 1.0.0 | Release Date: 2026-11-05 -->

# pycognition

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0003--7848--6418-green.svg)](https://orcid.org/0009-0003-7848-6418)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10000000.svg)](https://doi.org/10.5281/zenodo.10000000)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **A Dual-Process Cognitive Architecture Integrating Deterministic Procedural Execution and Deliberative LLM Synthesis**

`pycognition` is an open-source neurosymbolic framework formalizing Daniel Kahneman's **Dual-Process Cognitive Theory** for autonomous software agents. 

Contemporary agent frameworks (e.g., ReAct, AutoGen, CrewAI, LangChain) uniformly route deterministic and repetitive sub-tasks through cloud-hosted foundation model APIs. This causes severe latency inflation (1,500–5,000 ms), compounding token expenses, and non-deterministic execution drift. `pycognition` resolves this fundamental bottleneck by operating as an adaptive **Just-In-Time (JIT) compiler for natural language intents**: it deliberates on a task once, automatically synthesizes verified Python scripts, and hot-loads them into procedural memory for sub-millisecond execution at zero token cost.

---

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [The JIT Compilation & Amortized Inference Paradigm](#the-jit-compilation--amortized-inference-paradigm)
- [Validated Empirical Benchmarks (N = 100)](#validated-empirical-benchmarks-n--100)
- [Defensive Security & Sandboxing](#defensive-security--sandboxing)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quickstart](#quickstart)
- [Repository Structure](#repository-structure)
- [Scientific Preprint & Citation](#scientific-preprint--citation)
- [License & Author](#license--author)

---

## Architectural Overview

```
                       +-----------------------------+
                       |    Incoming Task T (JSON)   |
                       +-----------------------------+
                                      |
                                      v
                           +--------------------+
                           |    MetaArbiter     | <--- Cosine Sim (theta >= 0.55)
                           +--------------------+
                                  /      \
                Similarity >= theta        Similarity < theta
                                /          \
                               v            v
       +-----------------------------+   +-----------------------------+
       |          SYSTEM 1           |   |          SYSTEM 2           |
       |    (Procedural Execution)   |   |   (Deliberative Synthesis)  |
       +-----------------------------+   +-----------------------------+
       | • ProceduralRunner          |   | • LLMDeliberator (DeepSeek) |
       | • Native Python Functions   |   | • Chain-of-Thought (CoT)    |
       | • Latency: ~0.292 ms        |   | • Latency: ~3,307 ms        |
       | • Token Cost: 0 tokens      |   | • Token Cost: ~643 tokens   |
       +-----------------------------+   +-----------------------------+
                      ^                                 |
                      |      Skill Crystallization      |
                      |      =====================      |
                      |      1. Code & Test Synthesis   |
                      |      2. AST Security Audit      |
                      |      3. Isolated Pytest Sandbox |
                      |                                 v
                      +----------------------- [SkillRegistry]
```

### Core Components

1. **System 1 (Procedural Tier):**
   - **`ProceduralRunner`:** Executes compiled, type-annotated Python subroutines in-process via dynamic `importlib` bindings.
   - **Performance:** Mean execution latency of **0.292 ms** (down to 0.10 ms) with **strictly 0 API token expenditure**.
2. **System 2 (Deliberative Tier):**
   - **`LLMDeliberator`:** Handles novel task classes, open-ended semantic reasoning, and deep Chain-of-Thought (CoT) inference via OpenAI-compatible endpoints (default: `DeepSeek-V3`).
3. **Metacognitive Arbitration:**
   - **`MetaArbiter`:** Selects execution track $a \in \{\mathcal{S}_1, \mathcal{S}_2\}$ by optimizing an expected utility function:
     $$U(a \mid T) = \mathbb{E}[Q(a, T)] - \lambda_c \cdot C(a) - \lambda_\ell \cdot L(a)$$
   - **`VectorStoreMemory`:** Performs term-frequency (TF) vector similarity matching with automatic `snake_case` identifier splitting and trigger prompt indexing ($\theta = 0.55$).
4. **Defensive Skill Crystallization:**
   - **`SkillCrystallizer`:** Automatically generates Pydantic v2 schemas, type-annotated Python implementation routines, and companion `pytest` test suites.
   - **`ASTSecurityValidator`:** Rejects unsafe Abstract Syntax Tree nodes (blocking unauthorized imports such as `os`, `sys`, `subprocess`, `socket`, `open`, `shutil`, and dynamic execution primitives like `eval`, `exec`).
   - **Subprocess Sandbox:** Executes generated unit tests inside an isolated temporary directory guarded by a strict 15-second execution timeout.
   - **`SkillRegistry`:** Manages zero-downtime hot-reloading of admitted modules directly into active memory.

---

## The JIT Compilation & Amortized Inference Paradigm

Traditional agent evaluations naively compare a sub-millisecond compiled script directly against an LLM API call, falsely claiming "19,000x speedups" while ignoring the upfront software development time.

In `pycognition`, software routines are not assumed to exist a priori. The framework operates under a **realistic three-tier performance model**:

1. **Tier 1 — Marginal Procedural Speedup ($S_{\text{marginal}}$):** Once compiled, System 1 subroutines run in **0.292 ms** compared to **3,307.41 ms** for an uncompiled algorithmic LLM call (**11,326.7x marginal speedup**) and **5,580.36 ms** across all System 2 calls (**19,103.9x**).
2. **Tier 2 — Script Development Overhead & Per-Skill Break-Even ($k$):** On the first task encounter, the agent solves the problem and executes the crystallization pipeline (code synthesis, AST security audit, and sandboxed unit tests), taking an average of **7,192.20 ms** (total cold-start latency: **10,499.60 ms** or $\approx 10.50\text{ s}$).
   - **Ideal Break-Even:** When code passes tests on the first try, the compilation penalty ($\Delta L = 7,192.20 - 0.292 = 7,191.91\text{ ms}$) is fully amortized by the **4th invocation ($k = 4$)**:
     $$k \ge 1 + \frac{L_{\text{cryst}} - \bar{L}_{\mathcal{S}_1}}{L_{\text{base}} - \bar{L}_{\mathcal{S}_1}} = 1 + \frac{7\,192.20 - 0.292}{3\,307.41 - 0.292} \approx 3.175 \implies \mathbf{k = 4}$$
   - **Effective Break-Even:** Accounting for the empirical 36.2% sandbox rejection rate ($47 / 30 \approx 1.567$ attempts per admitted skill, $L_{\text{cryst,eff}} = 11,267.78\text{ ms}$), effective break-even occurs at **$k = 5$ invocations**.
3. **Tier 3 — Workload-Level Progression ($N = 100$ Tasks):**
   - **Asynchronous Mode:** When code synthesis runs in the background, user-perceived response time on 85 algorithmic tasks dropped from **281.13 s to 155.46 s (1.81x faster, -44.7% execution time)**.
   - **Synchronous Cluster Break-Even ($N^*$):** In a blocking setup including all 47 code compilation cycles (338.03 s), the net time deficit after 100 tasks is $212.36\text{ s}$. At the steady-state Quartile 4 procedural rate (71.4% of algorithmic queries), full synchronous cluster break-even converges at **$N^* \approx 207$ tasks**.

---

## Validated Empirical Benchmarks (N = 100)

Evaluated across a benchmark trace of **100 heterogeneous operational requests** (85 algorithmic tasks governed by a power-law Zipf distribution across 12 functional classes, alongside 15 unstructured conceptual Chain-of-Thought deliberations):

| Performance Dimension | Pure Frontier LLM Baseline | pycognition (Dual-Process) | Empirical Delta / Gain |
| :--- | :---: | :---: | :---: |
| **System 1 Marginal Latency** | 3,307.41 ms (algo) | **0.292 ms** (min 0.10 ms) | **11,326.7x faster** (sub-millisecond) |
| **Script Synthesis & Testing Latency** | 0 ms (no synthesis) | **7,192.20 ms** (mean) | JIT compilation investment |
| **Total Cold-Start Latency** | 3,307.41 ms | **10,499.60 ms** ($\approx 10.5\text{ s}$) | Initial learning overhead ($0.31\times$) |
| **Per-Skill Break-Even Point ($k$)** | N/A | **$k = 4$** (ideal) / **$k = 5$** (effective) | Fully amortized after 4–5 calls |
| **Marginal Speedup Factor** | 1.0x | **11,326.7x** (algo) / **19,103.9x** (overall) | Asymptotic performance limit |
| **85 Algorithmic Tasks Execution Time** | 281.13 s | **155.46 s** (asynchronous) | **1.81x speedup** (-44.7% execution time) |
| **Synchronous Wall-Clock Time** | 281.13 s | **493.49 s** (incl. 47 compilation runs) | Capital investment phase at $N = 100$ |
| **System Break-Even Horizon ($N^*$)** | N/A | **$N^* \approx 207$ tasks** | Full cluster wall-clock payback |
| **Cumulative Token Expenditure** | 87,061 tokens | **53,978 tokens** | **-38.0% immediate token reduction** |
| **Quartile 4 System 1 Coverage (Q4)** | 0.0% | **71.4%** (15 of 21 algorithmic) | Sustained procedural consolidation |
| **Sandbox Verification Yield** | N/A | **63.8% admitted** (30 of 47) | **100% System 1 memory fidelity** |

### Per-Skill Speedup Scaling $S(k)$

$$\text{Speedup } S(k) = \frac{k \cdot L_{\text{base}}}{L_{\text{base}} + L_{\text{cryst}} + (k - 1) \cdot \bar{L}_{\mathcal{S}_1}} = \frac{k \cdot 3\,307.41\text{ ms}}{10\,499.60\text{ ms} + (k - 1) \cdot 0.292\text{ ms}}$$

* **$k = 1$:** $0.31\times$ (temporal learning penalty)
* **$k = 2$:** $0.63\times$
* **$k = 3$:** $0.94\times$
* **$k = 4$:** **$1.26\times$ (Ideal break-even reached)**
* **$k = 5$:** **$1.57\times$ (Effective break-even reached with 36.2% sandbox rejects)**
* **$k = 10$:** $3.15\times$
* **$k = 50$:** $15.73\times$
* **$k = 100$:** $31.41\times$
* **$k \to \infty$:** Asymptotic limit of **$11,326.7\times$**

---

## Defensive Security & Sandboxing

`pycognition` **never** blindly executes model-generated code via `eval()` or unconstrained `exec()`:

1. **Static AST Inspection:** The synthesized Python source is parsed into an Abstract Syntax Tree prior to file persistence. Any prohibited AST nodes (`Import`, `ImportFrom`, or `Call` targeting blacklisted identifiers such as `os`, `sys`, `subprocess`, `socket`, `open`, `shutil`, `eval`, `exec`) trigger an immediate halt.
2. **Subprocess Isolation:** Generated test suites are written alongside candidate scripts into isolated ephemeral directories and executed via `pytest` inside an independent OS subprocess.
3. **Execution Quotas:** Subprocesses enforce strict memory constraints and a hard 15-second execution timeout ($t = 15.0\text{ s}$) to neutralize algorithmic complexity and infinite-loop denial-of-service vulnerabilities.
4. **Quarantine & Memory Invariance:** In our trials, **17 of 47 candidate routines (36.2%) were intercepted and rejected by the sandbox**:
   - 6 rejections: Degrees-of-freedom mismatches in variance calculation ($N$ vs. $N-1$ with Bessel's correction in z-score detection) and unhandled zero-variance divisions.
   - 4 rejections: Boundary invariants in IPv4 parsing (regular expressions permitting octet values $> 255$).
   - 4 rejections: Nested bracket grammar parsing mismatches.
   - 3 rejections: Floating-point precision tolerances in financial annuity calculations.
   *Rejection prevented silent regressions:* **100% of all 38 subsequent System 1 invocations succeeded without runtime errors**.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Operating System: Linux (Ubuntu 20.04+), macOS, or Windows 10/11

### Step 1. Clone & Setup Virtual Environment

#### On Windows (PowerShell / CMD):
```cmd
git clone https://github.com/MasterUaKi/pycognition.git
cd pycognition

python -m venv .venv
.venv\Scripts\activate
```

#### On Linux / macOS:
```bash
git clone https://github.com/MasterUaKi/pycognition.git
cd pycognition

python3 -m venv .venv
source .venv/bin/activate
```

### Step 2. Install Dependencies
```bash
# Install core package in editable mode
pip install -e .

# Install development, test, and benchmarking dependencies
pip install -e ".[dev,test]"
```

---

## Configuration

Configure environment variables via CLI or create a `.env` file in the project root:

```bash
# LLM Inference Endpoint (OpenAI-compatible)
DEEPSEEK_API_KEY="your-api-key-here"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
PYCOGNITION_MODEL="deepseek-chat"

# Metacognitive Arbiter & Memory
PYCOGNITION_ARBITER_THRESHOLD="0.55"      # Routing cosine threshold theta
PYCOGNITION_SKILLS_DIR="./skills_registry" # Directory for persisted skill modules

# Execution Sandbox Limits
PYCOGNITION_SANDBOX_TIMEOUT="15.0"        # Subprocess pytest timeout in seconds
```

---

## Quickstart

```python
import asyncio
from pycognition.runtime import DualProcessRuntime
from pycognition.schemas import TaskRequest

async def main():
    # 1. Initialize runtime (loads persisted skills from registry)
    runtime = DualProcessRuntime()

    # 2. Define an algorithmic task
    task = TaskRequest(
        prompt="calculate haversine distance between two coordinates in km",
        payload={
            "lat1": 52.728,
            "lon1": 8.289,
            "lat2": 53.079,
            "lon2": 8.801
        }
    )

    # 3. Call 1 (Cold Start):
    # Routed to System 2. The LLM resolves the task and crystallizes a
    # verified, AST-audited Python module in the background sandbox.
    res1 = await runtime.run(task)
    print(f"Call 1 Track:   {res1.track_used}")          # system_2
    print(f"Call 1 Latency: {res1.latency_ms:.2f} ms")   # ~3,300 ms
    print(f"Call 1 Result:  {res1.result}")

    # 4. Call 2 (Warm Execution):
    # MetaArbiter detects existing skill signature. Dispatches directly
    # to System 1 for compiled procedural execution.
    res2 = await runtime.run(task)
    print(f"Call 2 Track:   {res2.track_used}")          # system_1
    print(f"Call 2 Latency: {res2.latency_ms:.3f} ms")   # ~0.29 ms (11,000x speedup!)
    print(f"Call 2 Result:  {res2.result}")
    print(f"Tokens Used:    {res2.tokens_used}")         # 0 tokens!

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Repository Structure

```text
pycognition/
├── pyproject.toml              # PEP 621 / hatchling build specification
├── README.md                   # Canonical documentation
├── LICENSE                     # GNU Lesser General Public License v3.0
├── src/
│   └── pycognition/
│       ├── __init__.py
│       ├── runtime.py          # DualProcessRuntime: orchestration engine
│       ├── arbiter.py          # MetaArbiter: utility-theoretic routing
│       ├── memory.py           # VectorStoreMemory: TF-vector indexing
│       ├── procedural.py       # ProceduralRunner: System 1 execution tier
│       ├── deliberator.py      # LLMDeliberator: System 2 reasoning tier
│       ├── crystallizer.py     # SkillCrystallizer: code & test generation
│       ├── validator.py        # ASTSecurityValidator: static AST security
│       ├── registry.py         # SkillRegistry: zero-downtime hot-reloading
│       └── schemas.py          # Pydantic v2 data models and contracts
├── tests/
│   ├── test_arbiter.py
│   ├── test_ast_validator.py
│   ├── test_crystallizer.py
│   └── test_procedural_runner.py
├── scripts/
│   ├── run_experiment_100.py   # Benchmark reproduction harness
│   └── export_preprints.py     # Trilingual academic PDF compiler
└── skills_registry/            # Storage registry for crystallized Python routines
```

---

## Scientific Preprint & Citation

The architecture, mathematical formalization, and benchmark traces are published as an open-access scientific preprint (available in English, German, and Russian):

```bibtex
@article{riabtsev2026pycognition,
  author       = {Riabtsev, Oleh},
  title        = {pycognition: A Dual-Process Cognitive Architecture Integrating Deterministic Procedural Execution and Deliberative LLM Synthesis},
  institution  = {Universit{\"a}t Vechta, Referat Forschung, Nachwuchsf{\"o}rderung und Transfer (RFNT)},
  year         = {2026},
  month        = {11},
  doi          = {10.5281/zenodo.10000000},
  url          = {https://github.com/MasterUaKi/pycognition}
}
```

---

## License & Author

This software is released under the **GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)**. See the [LICENSE](LICENSE) file for complete details.

* **Author:** Oleh Riabtsev
* **Affiliation:** Referat Forschung, Nachwuchsförderung und Transfer (RFNT), Universität Vechta, Germany
* **ORCID:** [0009-0003-7848-6418](https://orcid.org/0009-0003-7848-6418)
* **Repository:** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)