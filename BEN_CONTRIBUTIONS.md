# Ben's Contribution & Experience Statements

---

## Ben Blake — Backend & Infrastructure

### Technical Contributions

| File | Description | Commit |
|------|-------------|--------|
| `src/agents/schema_linker.py` | Schema Linker agent using Cortex Search for semantic RAG over table metadata with FK-aware supplementation | [`c6fe6c8`](https://github.com/ben-blake/cs5542-lab07/commit/c6fe6c8) |
| `src/agents/sql_generator.py` | SQL Generator agent that prompts Cortex LLM with linked schema context to produce SQL | [`1e1a11e`](https://github.com/ben-blake/cs5542-lab07/commit/1e1a11e) |
| `src/agents/validator.py` | Validator agent that executes generated SQL, detects errors, and triggers self-correction loops | [`6f33c5f`](https://github.com/ben-blake/cs5542-lab07/commit/6f33c5f) |
| `src/utils/snowflake_conn.py` | Snowflake Snowpark session manager with singleton pattern and key-pair authentication support | [`5cf0bd5`](https://github.com/ben-blake/cs5542-lab07/commit/5cf0bd5) |
| `src/utils/config.py` | YAML-based configuration loader for model, search, and pipeline parameters | [`f2268d3`](https://github.com/ben-blake/cs5542-lab07/commit/f2268d3) |
| `src/utils/logger.py` | Structured logging utility writing to `logs/pipeline.log` | [`971311b`](https://github.com/ben-blake/cs5542-lab07/commit/971311b) |
| `scripts/ingest_data.py` | End-to-end data ingestion: DDL execution, staged CSV upload, COPY INTO, and validation | [`61babdf`](https://github.com/ben-blake/cs5542-lab07/commit/61babdf) |
| `scripts/build_metadata.py` | Metadata builder that uses Cortex LLM to generate column descriptions and synonyms for RAG | [`2a7bf36`](https://github.com/ben-blake/cs5542-lab07/commit/2a7bf36) |
| `snowflake/01_setup.sql` | Database, schema, warehouse, and stage setup DDL | [`693af32`](https://github.com/ben-blake/cs5542-lab07/commit/693af32) |
| `snowflake/02_olist_tables.sql` | Olist dataset table definitions (9 tables) | [`693af32`](https://github.com/ben-blake/cs5542-lab07/commit/693af32) |
| `snowflake/03_superstore.sql` | Superstore dataset table definition | [`693af32`](https://github.com/ben-blake/cs5542-lab07/commit/693af32) |
| `snowflake/04_metadata.sql` | Metadata schema and `TABLE_DESCRIPTIONS` table DDL | [`693af32`](https://github.com/ben-blake/cs5542-lab07/commit/693af32) |
| `snowflake/05_cortex_search.sql` | Cortex Search Service creation over `TABLE_DESCRIPTIONS` | [`693af32`](https://github.com/ben-blake/cs5542-lab07/commit/693af32) |
| `config.yaml` | Central configuration for model selection, search parameters, and pipeline settings | [`00187b5`](https://github.com/ben-blake/cs5542-lab07/commit/00187b5) |
| `reproduce.sh` | Full reproducibility script orchestrating venv setup, ingestion, metadata, search service, evaluation, and artifact collection | [`34cbd68`](https://github.com/ben-blake/cs5542-lab07/commit/34cbd68) |
| `requirements.txt` | Pinned Python dependencies for deterministic installs | [`0e76ad2`](https://github.com/ben-blake/cs5542-lab07/commit/0e76ad2) |
| `.env.example` | Template for required Snowflake environment variables | [`20aee32`](https://github.com/ben-blake/cs5542-lab07/commit/20aee32) |
| `.gitignore` | Git ignore rules for venv, credentials, logs, and data files | [`38922fb`](https://github.com/ben-blake/cs5542-lab07/commit/38922fb) |
| `RELATED_WORK_REPRO.md` | Analysis of related work and reproduction findings | [`b92355f`](https://github.com/ben-blake/cs5542-lab07/commit/b92355f) |
| `REPRO_AUDIT.md` | Reproducibility audit checklist and compliance report | [`f914769`](https://github.com/ben-blake/cs5542-lab07/commit/f914769) |
| `.github/workflows/ci.yml` | GitHub Actions CI running smoke tests on push/PR (Python 3.10, 3.11) | [`07ddfda`](https://github.com/ben-blake/cs5542-lab07/commit/07ddfda) |

### Challenges Encountered

The biggest challenge was making the SQL execution pipeline handle Snowflake DDL scripts reliably. Splitting SQL files by semicolons seemed simple, but comment lines preceding statements (e.g., `-- Section header` before `USE SCHEMA RAW;`) caused the parser to skip critical context-setting commands, which broke downstream `CREATE STAGE` statements. Debugging this required tracing through the exact split output to realize that `statement.startswith('--')` was discarding multi-line blocks that contained both comments and real SQL.

Output buffering through `tee` in `reproduce.sh` made scripts appear to hang — Python buffers stdout when it detects a pipe, so progress output was invisible until the script finished. The fix (`PYTHONUNBUFFERED=1`) was simple but diagnosing the root cause took time.

Getting the Cortex Search Service to work end-to-end required fully qualifying the service name (`ANALYTICS_COPILOT.METADATA.SCHEMA_SEARCH_SERVICE`) since the Snowpark session connects at the database level without a default schema.

### Lessons on Reproducibility

Reproducibility requires eliminating every implicit assumption. The session schema context issue taught me that "works in the Snowflake UI" does not mean "works in an automated script" — the UI carries session state that scripts do not. Every `USE DATABASE`, `USE SCHEMA`, and `USE WAREHOUSE` must be explicit.

The `reproduce.sh` script evolved through multiple failures into something that truly runs cold-start. Each bug — buffering, stale artifacts, missing DDL steps, unexecuted search service creation — represented an assumption that was obvious to the developer but invisible to a fresh environment. Reproducibility is achieved by systematically surfacing and codifying these assumptions.

### Agentic AI Influence on Workflow

Claude Code was instrumental in building the multi-agent architecture. The schema linker's Cortex Search integration, the validator's self-correction loop, and the metadata builder's LLM-driven description generation were all developed through an iterative conversation with Claude Code — describing the desired behavior, reviewing generated code, and refining edge cases.

For debugging, Claude Code's ability to read error output, trace through code paths, and suggest targeted fixes dramatically reduced iteration time. The SQL parser bug, the output buffering issue, and the Cortex Search qualification fix were all diagnosed and resolved within single conversation turns. The agentic workflow shifted my role from writing code to directing and reviewing — a more efficient use of domain knowledge.

### Reproducing Related Work

Reproducing Snowflake's Cortex Analyst examples revealed the gap between demo code and production-grade pipelines. The official examples assume a pre-configured environment with correct roles, warehouses, and schemas already active. Building `reproduce.sh` to handle all of this from scratch deepened my understanding of what "reproducible" really means — it is not enough for code to be correct; the entire environment setup must be scripted and idempotent. This experience directly informed the design of every step in our pipeline.
