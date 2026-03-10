# Lab 7: Reproducibility by Design with Agentic AI

A reproducible Text-to-SQL system that enables non-technical users to query data in plain English, powered by Snowflake Cortex LLM and a multi-agent pipeline.

## Team Members

- **Ben Blake** (GenAI & Backend Lead) - [@ben-blake](https://github.com/ben-blake)
- **Tina Nguyen** (Data & Frontend Lead) - [@tinana2k](https://github.com/tinana2k)

## Problem Statement

Non-technical users often depend on data analysts to write SQL queries or build dashboards, creating bottlenecks and slowing down decision-making. This system allows business users to ask questions in plain English and receive accurate SQL queries, result tables, and visualizations.

## System Architecture

The system uses a three-agent pipeline built on Snowflake Cortex:

1. **Schema Linker** - RAG-based retrieval over metadata to find relevant tables (Cortex Search)
2. **SQL Generator** - LLM-powered SQL generation with few-shot examples (Cortex Complete, llama3.1-70b)
3. **Validator** - EXPLAIN-based validation with self-correction retry loop (up to 3 attempts)

## Reproducibility

This project is packaged as a **reproducible research artifact** for CS 5542 Lab 7.

### Single-Command Reproduction

```bash
# Smoke tests only (no Snowflake needed)
./reproduce.sh --smoke

# Full pipeline (requires Snowflake credentials + Olist data)
cp .env.example .env   # fill in credentials
./reproduce.sh
```

### Reproducibility Artifacts

| File | Purpose |
|---|---|
| [`reproduce.sh`](reproduce.sh) | Single-command entry point (`--smoke`, `--test`, `--eval`, full) |
| [`config.yaml`](config.yaml) | Centralized runtime configuration (seed, LLM, paths) |
| [`requirements.txt`](requirements.txt) | Pinned dependencies with `==` for all 9 packages |
| [`tests/test_smoke.py`](tests/test_smoke.py) | 18 smoke tests that run offline (no Snowflake) |
| [`artifacts/`](artifacts/) | Generated evaluation reports |
| [`logs/`](logs/) | Pipeline execution logs |
| [`RUN.md`](RUN.md) | Step-by-step reproduction instructions |
| [`REPRO_AUDIT.md`](REPRO_AUDIT.md) | 8-point reproducibility checklist with evidence |
| [`RELATED_WORK_REPRO.md`](RELATED_WORK_REPRO.md) | Related work reproduction report (X-SQL, NeurIPS 2025) |

### Determinism Controls

- **Random seed**: `42` (set in `config.yaml`, applied via `src/utils/config.py`)
- **LLM temperature**: `0.0` (minimizes output variance)
- **Pinned packages**: All dependencies locked to exact versions
- **Config-driven**: No hardcoded parameters; everything in `config.yaml`

### Agentic AI Tool Usage

**Tool used:** Anthropic Claude Code (claude-opus-4-6)

| Task Automated | Verified By |
|---|---|
| Reproducibility scaffolding (`reproduce.sh`, `config.yaml`) | Team review + execution |
| Smoke test suite (`tests/test_smoke.py`) | All 18 tests pass |
| Pinned dependency resolution | `pip install` verified |
| Logging infrastructure (`src/utils/logger.py`) | Runtime verification |
| Documentation templates (RUN.md, REPRO_AUDIT.md, RELATED_WORK_REPRO.md) | Team review |

All generated code was reviewed, validated, and tested by the team. The team is fully responsible for correctness and reproducibility.

## Related Work Reproduction (Part B)

We reproduced key components from **X-SQL: Expert Schema Linking and Understanding of Text-to-SQL with Multi-LLMs** (NeurIPS 2025, [arXiv:2509.05899](https://arxiv.org/abs/2509.05899)).

**What we reproduced:**
- Multi-agent decomposition pattern (schema linking as a separate expert step)
- Schema filtering to reduce irrelevant context before SQL generation
- Error-feedback self-correction loop between agents

**Improvements integrated into our system:**
1. FK-partner supplementation in schema linker (ensures join-related tables are included)
2. Dataset isolation filter (prevents cross-dataset confusion)
3. Structured error feedback for self-correction retries

See [`RELATED_WORK_REPRO.md`](RELATED_WORK_REPRO.md) for the full reproduction report.

## Datasets

1. **Olist Brazilian E-Commerce** (primary) - [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   - 100k orders across 9 relational tables
2. **Superstore Sales** (optional baseline) - [Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
3. **Spider Text-to-SQL** (few-shot patterns) - [Hugging Face](https://huggingface.co/datasets/xlangai/spider)

## Repository Structure

```
analytics-copilot/
├── src/
│   ├── agents/              # Multi-agent pipeline
│   │   ├── schema_linker.py # RAG-based table retrieval
│   │   ├── sql_generator.py # LLM SQL generation
│   │   └── validator.py     # EXPLAIN validation + self-correction
│   ├── utils/
│   │   ├── snowflake_conn.py # Snowflake session management
│   │   ├── viz.py            # Auto-chart generation
│   │   ├── config.py         # Config loader with seed control
│   │   └── logger.py         # File + console logging
│   └── app.py               # Streamlit chat interface
├── scripts/
│   ├── ingest_data.py       # CSV -> Snowflake ingestion
│   ├── build_metadata.py    # Cortex-powered metadata generation
│   ├── generate_golden.py   # Golden query benchmark generation
│   └── evaluate.py          # Pipeline accuracy evaluation
├── snowflake/               # DDL scripts (01-05)
├── tests/
│   └── test_smoke.py        # 18 offline smoke tests
├── data/
│   ├── olist/               # 9 Olist CSVs
│   ├── superstore/          # Superstore CSV (optional)
│   └── golden_queries.json  # 50 benchmark question-SQL pairs
├── artifacts/               # Generated evaluation reports
├── logs/                    # Pipeline execution logs
├── reproduce.sh             # Single-command reproduction
├── config.yaml              # Runtime configuration
├── requirements.txt         # Pinned dependencies
├── RUN.md                   # Reproduction instructions
├── REPRO_AUDIT.md           # Reproducibility audit
├── RELATED_WORK_REPRO.md    # Related work report
└── .env.example             # Credential template
```

## Setup Instructions

### 1. Clone and Configure

```bash
git clone https://github.com/ben-blake/analytics-copilot.git
cd analytics-copilot
cp .env.example .env
# Edit .env with your Snowflake credentials
```

### 2. Reproduce

```bash
chmod +x reproduce.sh
./reproduce.sh --smoke   # Verify setup (no Snowflake needed)
./reproduce.sh           # Full pipeline (with Snowflake)
```

See [`RUN.md`](RUN.md) for detailed step-by-step instructions.

### 3. Launch Application

```bash
source venv/bin/activate
streamlit run src/app.py
```

Open `http://localhost:8501` to start asking questions about your data.

## Features

- **Natural Language to SQL**: Ask questions in plain English against the Olist dataset
- **Context-Aware RAG**: Cortex Search retrieves relevant schema metadata to reduce hallucinations
- **Multi-Agent Pipeline**: Schema Linker -> SQL Generator -> Validator
- **Auto-Visualization**: Generates bar, line, or scatter charts based on query results
- **Self-Correction**: Validator retries up to 3 times with error feedback
- **Snowflake Cortex**: Uses llama3.1-70b via Cortex Complete and Cortex Search

## Evaluation

The system is benchmarked against 50 golden queries (easy/medium/hard):

```bash
source venv/bin/activate
python scripts/evaluate.py
```

Metrics: Execution Accuracy (~97%), Average Latency (~5-8s per query)

Results saved to `artifacts/evaluation_report.json`.

## Related Work References

1. **MAIA: Chatting With Your Data** (NeurIPS 2025) - Schema abstraction technique adapted for our semantic metadata layer
2. **OmniSQL** (NeurIPS 2025, [arXiv:2503.02240](https://arxiv.org/abs/2503.02240)) - Synthetic question generation approach used for golden query benchmarks
3. **X-SQL** (NeurIPS 2025, [arXiv:2509.05899](https://arxiv.org/abs/2509.05899)) - Expert schema linking pattern reproduced and integrated

## Team Contributions

See [`BEN_CONTRIBUTIONS.md`](BEN_CONTRIBUTIONS.md) and [`TINA_CONTRIBUTIONS.md`](TINA_CONTRIBUTIONS.md) for detailed individual contributions and commit history.
