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

The full regression suite after DQ integration passed:

```text
23 passed
```

## 3. Data Quality Tests

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

## 4. Source Integrity Test

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

## 5. Reconciliation Test

Source counts were compared with PostgreSQL counts.

Result:

```text
RECONCILIATION : PASS
```

## 6. Idempotency Test

A loaded match was processed again and its business-row counts remained unchanged.

Result:

```text
IDEMPOTENCY : PASS
```

## 7. Data Quality Audit Test

A real warning case was processed and persisted to `etl_file_quality_issue`.

A synthetic ERROR audit case was also tested and then removed so test data did not remain in the production-like database.

## 8. Recommended Developer Check

Before a logical commit:

```powershell
pytest -q
```

For ETL changes, also run the relevant ingestion/reconciliation checks.

## 9. Testing Principle

A feature is not considered complete merely because the code executes.

Completion requires:

**Implementation + tests + verification + documentation**
