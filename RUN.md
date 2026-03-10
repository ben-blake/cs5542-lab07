# RUN.md - How to Reproduce Analytics Copilot

## Quick Start (Smoke Test Only - No Snowflake Needed)

```bash
git clone https://github.com/ben-blake/cs5542-lab07.git
cd cs5542-lab07
chmod +x reproduce.sh
./reproduce.sh --smoke
```

This verifies that all modules import correctly, config loads, golden queries parse, and visualization logic works - all without a Snowflake connection.

## Full Reproduction (Requires Snowflake)

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Snowflake Account | Trial or enterprise (Cortex-enabled) |
| OS | macOS, Linux, or WSL |

### Step 1: Clone and Configure

```bash
git clone https://github.com/ben-blake/cs5542-lab07.git
cd cs5542-lab07
cp .env.example .env
# Edit .env with your Snowflake credentials
```

### Step 2: Download Data

Download the Olist dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and unzip into `data/olist/`. You should have 9 CSV files.

### Step 3: Run

```bash
chmod +x reproduce.sh
./reproduce.sh
```

This single command will:
1. Create a Python virtual environment
2. Install pinned dependencies from `requirements.txt`
3. Run smoke tests
4. Ingest data into Snowflake
5. Generate semantic metadata using Cortex LLM
6. Run evaluation against golden queries
7. Save artifacts and logs

### Step 4: Launch the App (Optional)

```bash
source venv/bin/activate
streamlit run src/app.py
```

## Run Modes

| Command | What It Does |
|---|---|
| `./reproduce.sh` | Full pipeline (ingest + metadata + eval) |
| `./reproduce.sh --smoke` | Smoke tests only (no Snowflake) |
| `./reproduce.sh --test` | Same as --smoke |
| `./reproduce.sh --eval` | Full pipeline including evaluation |

## Output Structure

```
artifacts/          # Evaluation reports and results
logs/               # Pipeline logs (ingest, metadata, evaluation, smoke tests)
  pipeline.log      # Runtime log from Python logging
  smoke_test.log    # Smoke test output
  ingest.log        # Data ingestion output
  metadata.log      # Metadata generation output
  evaluation.log    # Evaluation benchmark output
```

## Configuration

All runtime parameters are in `config.yaml`:
- Random seed (42)
- LLM model and temperature
- Schema linker limits
- Evaluation settings
- Data and artifact paths

No hardcoded magic numbers in the codebase.

## Environment Determinism

- **Pinned dependencies**: `requirements.txt` uses `==` for all packages
- **Random seed**: Set in `config.yaml`, applied at startup
- **LLM temperature**: Set to 0.0 for deterministic generation
- **Config-driven**: All parameters externalized to `config.yaml`
