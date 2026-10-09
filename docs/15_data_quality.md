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

## 8. Analytics Data Semantics

The analytics layer applies explicit metric semantics to the normalized event data.

### Legal deliveries

For innings-level run-rate calculations, wides and no-balls are excluded from the legal-delivery denominator. Total delivery records remain available as a separate metric.

### Wickets lost

Innings wickets lost exclude `retired hurt`, because a retirement hurt is not treated as a dismissal/wicket lost for scorecard-style analytics.

These rules are analytical semantics rather than new ingestion DQ rules. They are documented here because they affect how downstream consumers interpret the trusted database facts.

## 8. Venue master-data observation

The loaded venue dimension contains name variants that may represent the same physical venue. Examples observed during Venue Analytics validation include:

- `Wankhede Stadium`
- `Wankhede Stadium, Mumbai`
- `M.Chinnaswamy Stadium`
- `M Chinnaswamy Stadium`

This is a **master-data standardization observation**, not an analytics calculation error. The current analytics layer intentionally does not silently merge these records because doing so without an explicit canonicalization rule could change historical aggregates.

A future venue-standardization step should define:
- canonical venue identity
- approved aliases
- matching rules
- historical backfill behavior
- tests proving that the resulting aggregation is intentional

## 9. Engineering Principle

Data quality is not only a gate.

It is also an observability mechanism.

A production pipeline should make it possible to identify:

- what was wrong
- where it was wrong
- how severe it was
- which file contained it
- which run processed it

## 9. Match Outcome Semantics

The trusted match model preserves source outcome semantics separately from ordinary winners:

| Field | Meaning |
|---|---|
| `winner_id` | Normal match winner, when present |
| `outcome_result = 'tie'` | Source-recorded tie |
| `outcome_result = 'no result'` | Source-recorded no-result match |
| `outcome_deciding_team_id` | Team recorded as deciding a tie through a Super Over/eliminator |

A deciding team is stored separately and does not convert a source-recorded tie into an ordinary win. Outcome values are parsed from source metadata rather than inferred from innings.

The backfill check covered 1,243 source files: **0 updated, 1,243 unchanged, 0 missing database records**.

## 10. Head-to-Head Analytical Semantics

H2H aggregation includes a match only when both requested teams appear in `match_team`. Results are classified consistently:
- `winner_id = Team A`: Team A win
- `winner_id = Team B`: Team B win
- `outcome_result = 'tie'`: tie
- `outcome_result = 'no result'`: no result

The deciding team for a Super Over/eliminator is not converted into an ordinary H2H win. Overall and season-wise aggregates are performed in PostgreSQL.

