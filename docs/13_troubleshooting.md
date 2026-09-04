# 13 Troubleshooting

## `conda` is not recognized in PowerShell

### Cause

Conda shell integration or PowerShell execution-policy configuration.

### Practice

Verify the environment through Anaconda Prompt and confirm:

```powershell
python -c "import sys; print(sys.executable)"
```

## `ModuleNotFoundError: No module named 'src'`

### Cause

A project module was executed directly from the scripts directory.

Avoid:

```powershell
python scripts\test_database_connection.py
```

Use:

```powershell
python -m scripts.test_database_connection
```

Run from the project root.

## `pip` appears to use the wrong Python

Verify:

```powershell
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```

The active paths should point to the Conda environment.

## PostgreSQL client not in PATH

Use the installed executable directly:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

## ETL file failure

Check:

1. ETL run status
2. `etl_file_log`
3. recorded stage
4. error message
5. data-quality issues linked through `file_log_id`

The pipeline is intentionally stage-aware so failures can be localized.

## Data-quality failure

Blocking DQ errors stop the affected file from loading.

Inspect:

```text
etl_file_quality_issue
```

using the related `file_log_id`.

Warnings do not block a valid load but remain auditable.

## Duplicate delivery concern

Do not assume source `ball_number` is a globally unique delivery key.

The database uses:

```text
innings_id + over_number + delivery_sequence
```

## Re-running ingestion

The loader is designed to be idempotent. Re-running an already loaded match should not create duplicate business rows.

If duplicates are suspected, verify counts before and after the rerun and inspect the relevant unique constraints.

## Git issue after changes

Before committing:

```powershell
git status
git diff
pytest -q
```

If a change is unrelated to the current task, do not bundle it into the same logical commit.
