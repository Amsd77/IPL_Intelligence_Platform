# Change Log

## 2026-08-22 — Project Foundation

### Project initialized

Created the initial project structure:

```text
data/
src/
tests/
notebooks/
scripts/
logs/
```

Created project configuration and documentation files.

### Python environment

Created Conda environment:

```text
IPL_Intelligence_Platform
```

Python:

```text
3.12.13
```

### Dataset

Added the Cricsheet IPL JSON dataset under:

```text
data/raw/cricsheet/
```

The dataset was profiled before database design.

### PostgreSQL

Verified PostgreSQL 17.6 and selected the dedicated database:

```text
ipl_intelligence
```

### SQLAlchemy connection

Created the reusable connection layer in:

```text
src/database/connection.py
```

## 2026-08-23 to 2026-08-26 — Data Engineering Foundation

Implemented and verified:

- PostgreSQL relational schema
- SQLAlchemy models
- Cricsheet source schema inspection
- JSON reader
- match parser
- structural validator
- transformation layer
- database loader
- ETL run/file audit logging

Important design decisions:

- normalize historical team aliases
- preserve delivery-level events
- use delivery sequence for delivery-position uniqueness
- separate ETL audit data from cricket facts

## 2026-09-03 — Data Quality and ETL Hardening

Implemented:

- explicit data-quality result model
- blocking ERROR rules
- non-blocking WARNING rules
- `etl_file_quality_issue` persistence
- file-level DQ audit integration

Verified DQ findings:

```text
DQ010 venue.city       51 WARNING
DQ011 player_of_match   9 WARNING
Total                  60 WARNING
Blocking errors         0
```

### Full ingestion

```text
Run ID     : 7
Discovered : 1243
Processed  : 1243
Successful : 1243
Failed     : 0
```

### Reconciliation

```text
matches       1,243 / 1,243
innings       2,514 / 2,514
deliveries  295,732 / 295,732
extras       16,255 / 16,255
wickets      14,705 / 14,705
RECONCILIATION : PASS
```

### Idempotency

Verified by rerunning match `1082591` without increasing its business-row counts.

Result:

```text
IDEMPOTENCY : PASS
```

### Regression tests

```text
23 passed
```

## Engineering Lessons

- Preserve raw source data.
- Profile data before designing schemas.
- Separate ingestion, validation, transformation, database, and application responsibilities.
- Use environment variables for secrets.
- Run project modules from the project root.
- Verify the actual Python executable before installing dependencies.
- Treat reconciliation as a gate before downstream analytics.
- Persist data-quality findings so production failures are diagnosable.
- Commit work in small, logical, reviewable units.
