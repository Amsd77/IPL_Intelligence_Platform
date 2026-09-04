# 15 Data Quality

## 1. Purpose

The data-quality layer protects the database from structurally or logically invalid match records while preserving non-blocking observations for audit.

## 2. Severity Model

### ERROR

An ERROR means the file should not proceed to transformation/loading.

Examples:

- invalid winner relationship
- invalid toss winner relationship
- invalid toss decision
- duplicate innings
- non-sequential innings
- invalid batting team
- impossible run relationship

### WARNING

A WARNING indicates incomplete or less-critical information.

Warnings do not block loading.

Examples:

- missing venue city
- missing player of match

## 3. Current Rules

| Rule | Description | Severity |
|---|---|---|
| DQ001 | Winner belongs to match teams | ERROR |
| DQ002 | Toss winner belongs to match teams | ERROR |
| DQ003 | Toss decision is valid | ERROR |
| DQ004 | Duplicate innings | ERROR |
| DQ005 | Sequential innings | ERROR |
| DQ006 | Batting team is valid | ERROR |
| DQ008 | `total_runs >= batter_runs` | ERROR |
| DQ009 | Player of match belongs to player list | WARNING |
| DQ010 | Venue city completeness | WARNING |
| DQ011 | Missing player of match | WARNING |

The earlier DQ007 delivery-position rule was deferred because source ball numbering can represent legitimate illegal deliveries in ways that make a simple `over_number + ball_number` uniqueness rule unsafe.

The database instead uses `delivery_sequence`.

## 4. Result Model

The validation layer returns:

```text
DataQualityResult
    |
    +-- issues
    +-- errors
    +-- warnings
    +-- is_valid
```

This keeps rule evaluation independent from the ETL orchestration.

## 5. Persistence

Persisted issues are stored in:

```text
etl_file_quality_issue
```

Each issue is linked to:

```text
etl_file_log.file_log_id
```

This allows a developer to answer:

> Which quality problems occurred in which file during which ETL run?

## 6. Current Full-Dataset Findings

```text
DQ010 : 51 WARNING
DQ011 :  9 WARNING
TOTAL : 60 WARNING
ERROR :  0
```

The warnings do not invalidate the loaded dataset because they are explicitly non-blocking.

## 7. Verification

A real warning case was processed and verified in the database.

A synthetic ERROR persistence case was also tested and removed afterward so test artifacts were not retained.

## 8. Engineering Principle

Data quality is not only a gate.

It is also an observability mechanism.

A production pipeline should make it possible to identify:

- what was wrong
- where it was wrong
- how severe it was
- which file contained it
- which run processed it
