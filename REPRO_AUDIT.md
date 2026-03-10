# REPRO_AUDIT.md - Reproducibility Audit Checklist

## Project: Analytics Copilot (Text-to-SQL with Snowflake Cortex)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Single-command execution | PASS | `./reproduce.sh` runs full pipeline |
| 2 | Pinned environment | PASS | `requirements.txt` uses `==` for all 8 packages |
| 3 | Randomness control | PASS | Seed 42 in `config.yaml`; LLM temperature 0.0 |
| 4 | Config-driven execution | PASS | `config.yaml` externalizes all parameters |
| 5 | Structured artifacts | PASS | `artifacts/` for reports, `logs/` for pipeline logs |
| 6 | Logging | PASS | `src/utils/logger.py` with file + console handlers |
| 7 | Smoke test | PASS | `tests/test_smoke.py` - 13 tests, no Snowflake needed |
| 8 | Documentation | PASS | README.md, RUN.md, REPRO_AUDIT.md, RELATED_WORK_REPRO.md |

## Detailed Audit

### 1. Single-Command Execution

- Script: `reproduce.sh`
- Supports modes: `--smoke` (offline), `--test`, `--eval`, full
- Creates venv, installs deps, runs tests, ingests data, evaluates
- Exit-on-error (`set -euo pipefail`)

### 2. Pinned Environment

- File: `requirements.txt`
- All 8 direct dependencies pinned with `==`
- Python version requirement: 3.10+ (documented in RUN.md)
- Virtual environment created fresh by `reproduce.sh`

### 3. Randomness / Determinism

- **Seed**: `config.yaml` -> `seed: 42`, applied via `src/utils/config.py`
- **LLM temperature**: `config.yaml` -> `llm.temperature: 0.0`
- **Note**: Full determinism is limited by the Snowflake Cortex LLM backend. LLM outputs may vary slightly across runs even with temperature 0.0, as the model runs server-side on Snowflake infrastructure. The seed controls Python-side randomness (e.g., any sampling or shuffling).

### 4. Config-Driven Execution

- File: `config.yaml`
- Covers: seed, Snowflake settings, LLM model, schema linker limits, evaluation parameters, data paths, logging configuration
- No hardcoded magic numbers in source code for configurable values

### 5. Structured Artifacts

- `artifacts/`: evaluation reports (JSON)
- `logs/`: pipeline execution logs
- `data/golden_queries.json`: benchmark dataset (version-controlled)
- `data/evaluation_report.json`: evaluation results

### 6. Logging

- Module: `src/utils/logger.py`
- Dual output: file (`logs/pipeline.log`) + console
- Configurable level and format via `config.yaml`
- Pipeline scripts log to individual files via `tee` in `reproduce.sh`

### 7. Smoke Test

- File: `tests/test_smoke.py`
- 13 test cases across 6 test classes
- Tests: imports, config loading, golden query validation, visualization, SQL extraction, input validation
- Runs without Snowflake connection
- Command: `python -m pytest tests/test_smoke.py -v`

### 8. Known Reproducibility Limitations

| Limitation | Mitigation |
|---|---|
| Snowflake Cortex LLM non-determinism | Temperature set to 0.0; golden queries pre-generated and version-controlled |
| Snowflake account required | Smoke tests work offline; credentials documented in .env.example |
| Kaggle data download manual | Download instructions in README.md and RUN.md |
| Cortex Search service provisioning time | Documented in reproducibility/README.md troubleshooting |

## Agentic AI Tool Usage

| Task | Tool Used | What Was Automated |
|---|---|---|
| Reproducibility scaffolding | Anthropic Claude Code (claude-opus-4-6) | Generated reproduce.sh, config.yaml, smoke tests, documentation templates |
| Pinned requirements | Anthropic Claude Code | Resolved and pinned exact package versions |
| Logging infrastructure | Anthropic Claude Code | Created logger module and config integration |
| Documentation | Anthropic Claude Code | Generated RUN.md, REPRO_AUDIT.md, RELATED_WORK_REPRO.md |

All generated code was reviewed and validated by the team. The team is responsible for correctness and reproducibility.
