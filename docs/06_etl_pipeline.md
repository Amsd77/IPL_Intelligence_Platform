# 06 ETL Pipeline

## 1. Objective

The ETL pipeline converts Cricsheet IPL JSON files into validated, transformed, and persisted PostgreSQL records.

## 2. Pipeline Stages

```text
DISCOVER
   |
READ
   |
PARSE
   |
VALIDATE
   |
DATA_QUALITY
   |
TRANSFORM
   |
LOAD
   |
AUDIT SUCCESS
```

Failures are recorded against the current stage.

## 3. Source Discovery

The pipeline discovers JSON files under:

```text
data/raw/cricsheet/ipl_json/
```

The current source contains:

```text
1,243 JSON match files
```

The source README is not treated as a match file because ingestion targets `*.json`.

## 4. Read

The JSON reader loads one source file without modifying it.

## 5. Parse

The parser converts source JSON into typed/domain records including:

- match
- teams
- players
- venue
- innings
- deliveries
- extras
- wickets

## 6. Structural Validation

The match validator checks structural assumptions before database loading.

Examples include:

- required match information
- valid participating teams
- valid innings structure
- valid delivery/player relationships

## 7. Data Quality

The DQ layer applies explicit rules.

Blocking examples:

- winner must belong to match teams
- toss winner must belong to match teams
- toss decision must be valid
- innings must be sequential
- batting team must belong to match teams
- total runs must not be less than batter runs

Non-blocking examples:

- missing venue city
- missing player of the match

## 8. Transformation

Validated domain records are converted into the package expected by the database loader.

Transformation is deliberately separate from parsing so source representation and persistence representation do not become tightly coupled.

## 9. Loading

The loader persists:

1. dimensions
2. match relationships
3. innings
4. deliveries
5. extras
6. wickets

The loader is designed to be idempotent.

## 10. ETL Audit

Every run records:

- ETL run status
- file processing status
- current stage
- success/failure
- processing duration
- data-quality issues

## 11. Full Ingestion Result

Verified full run:

```text
Discovered : 1243
Processed  : 1243
Successful : 1243
Failed     : 0
```

## 12. Reconciliation

Source and database counts were reconciled:

```text
matches       1,243   1,243   PASS
innings       2,514   2,514   PASS
deliveries  295,732 295,732   PASS
extras       16,255  16,255   PASS
wickets      14,705  14,705   PASS
```

## 13. Idempotency Verification

A previously loaded match was rerun.

Before and after business-row counts remained:

```text
innings     2
deliveries 248
extras      12
wickets    14
```

This confirms that retrying the same match does not duplicate those rows.

## 14. Operational Principle

A production ETL pipeline must be:

- repeatable
- observable
- auditable
- restartable
- validated
- reconciled

The current implementation establishes those foundations before analytics/ML work begins.
