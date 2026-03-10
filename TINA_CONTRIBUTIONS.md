# Tina's Contribution & Experience Statements

---

## Tina Nguyen — Frontend & Evaluation

### Technical Contributions

| File | Description | Commit |
|------|-------------|--------|
| `src/app.py` | Streamlit chat UI integrating all three agents into an interactive text-to-SQL interface | [`3309e3d`](https://github.com/ben-blake/cs5542-lab07/commit/3309e3d) |
| `src/utils/viz.py` | Automatic chart generation module using Altair, selecting chart types based on DataFrame column structure | [`e0403fa`](https://github.com/ben-blake/cs5542-lab07/commit/e0403fa) |
| `scripts/evaluate.py` | Evaluation harness that runs golden queries, compares results, and writes `artifacts/evaluation_report.json` | [`3fa3afc`](https://github.com/ben-blake/cs5542-lab07/commit/3fa3afc) |
| `scripts/generate_golden.py` | Script to generate the golden query benchmark set (`data/golden_queries.json`) | [`db59d79`](https://github.com/ben-blake/cs5542-lab07/commit/db59d79) |
| `data/golden_queries.json` | 50 curated benchmark queries (easy/medium/hard) with ground-truth SQL | [`2abf9e3`](https://github.com/ben-blake/cs5542-lab07/commit/2abf9e3) |
| `tests/test_smoke.py` | Smoke tests validating agent contracts, empty-input handling, and config loading | [`f812ac6`](https://github.com/ben-blake/cs5542-lab07/commit/f812ac6) |
| `README.md` | Project documentation covering setup, architecture, and usage | [`fe34af1`](https://github.com/ben-blake/cs5542-lab07/commit/fe34af1) |
| `RUN.md` | Quick-start run instructions for reviewers | [`a0daca4`](https://github.com/ben-blake/cs5542-lab07/commit/a0daca4) |

### Challenges Encountered

Building an evaluation framework that fairly measures SQL correctness was harder than expected. Two semantically equivalent queries can have completely different SQL text, so the evaluator had to compare result sets rather than string-matching. Wiring the Streamlit UI to display intermediate agent outputs (schema linking results, validation feedback) without cluttering the chat flow required careful state management with `st.session_state`.

### Lessons on Reproducibility

Designing the evaluation pipeline taught me that reproducibility is not just about re-running code — it requires deterministic benchmarks. The golden query set needed fixed difficulty labels and stable ground-truth SQL so that evaluation scores are comparable across runs. Pinning the Cortex LLM model (`llama3.1-70b`) in `config.yaml` rather than defaulting to "latest" was essential; model drift would silently change results.

### Agentic AI Influence on Workflow

Claude Code accelerated the Streamlit UI iteration cycle significantly. I described the desired chat layout and agent integration pattern, and it generated the session-state wiring and message rendering logic. It also helped draft the 50 golden queries by generating SQL for natural-language questions I wrote, which I then manually verified. The feedback loop — describe, generate, verify — was much faster than writing everything from scratch.

### Reproducing Related Work

Reproducing the Cortex Analyst approach from Snowflake's documentation revealed how much implicit setup knowledge exists in official tutorials. Steps like enabling Cortex functions, granting roles, and configuring search services were glossed over in the docs but critical for a cold-start reproduction. This made me appreciate how explicit our `reproduce.sh` pipeline needs to be — every assumption must be codified.
