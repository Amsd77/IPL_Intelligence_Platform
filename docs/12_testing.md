# 12 Testing

## 1. Testing Strategy

Testing is layered so failures can be isolated quickly.

```text
Unit tests
   |
Component/integration tests
   |
Pipeline tests
   |
Data reconciliation
   |
Idempotency verification
```

## 2. Current Test Coverage

The project currently has tests covering:

- parser behavior
- structural validation
- data-quality rules
- negative DQ cases
- database/ETL behavior
- player and team analytics
- match summary analytics
- match innings analytics

The full regression suite after the Analytics Foundation additions passed:

```text
45 passed
```

## 3. Analytics Tests

Match analytics tests cover successful result mapping, unknown-match behavior, and validation of invalid match IDs. Match innings tests cover innings result mapping, empty results for unknown matches, and invalid match ID validation.

The implementation was also validated against real PostgreSQL data across multiple matches, including matches containing wides/no-balls and wicket events. The validation confirmed that legal-delivery counts do not exceed total delivery counts and that innings run rates and wicket counts remain internally consistent.

## 4. Data Quality Tests

Positive tests verify that valid source matches pass.

Negative tests cover the current blocking and warning rules, including:

- DQ001
- DQ002
- DQ003
- DQ004
- DQ005
- DQ006
- DQ008
- DQ009
- DQ010
- DQ011

## 5. Source Integrity Test

The source was checked for:

- numeric match IDs
- duplicate IDs
- expected unique file identity

Result:

```text
JSON files found : 1243
Non-numeric IDs  : 0
Unique match IDs : 1243
Duplicate IDs    : 0
SOURCE INTEGRITY : PASS
```

## 6. Reconciliation Test

Source counts were compared with PostgreSQL counts.

Result:

```text
RECONCILIATION : PASS
```

## 7. Idempotency Test

A loaded match was processed again and its business-row counts remained unchanged.

Result:

```text
IDEMPOTENCY : PASS
```

## 8. Data Quality Audit Test

A real warning case was processed and persisted to `etl_file_quality_issue`.

A synthetic ERROR audit case was also tested and then removed so test data did not remain in the production-like database.

## 9. Recommended Developer Check

Before a logical commit:

```powershell
pytest -q
```

For ETL changes, also run the relevant ingestion/reconciliation checks.

## 10. Testing Principle

A feature is not considered complete merely because the code executes.

Completion requires:

**Implementation + tests + verification + documentation**
