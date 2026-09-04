# 02 Architecture

## 1. Architecture Goal

The platform is designed as a layered system where each responsibility is isolated.

The current implementation focuses on the data-engineering foundation. Analytics, ML, GenAI, RAG, API, UI, and deployment are downstream layers and are not yet implemented.

## 2. Current Data Flow

```text
Cricsheet IPL JSON
        |
        v
[Ingestion]
 JSON Reader
        |
        v
[Parsing]
 Match Parser
        |
        v
[Validation]
 Structural Validator
        |
        v
[Data Quality]
 DQ Rules
   |        |
 ERROR    WARNING
   |        |
 block    audit
   |        |
   +---+----+
       |
       v
[Transformation]
 Domain records -> database-ready package
       |
       v
[Database Loader]
 PostgreSQL
```

## 3. Application Layers

```text
src/
├── ingestion/
├── validation/
├── transformation/
├── database/
└── config/
```

### Ingestion

Reads source files without changing the raw source.

### Validation

Checks whether the parsed match structure is acceptable before loading.

### Transformation

Converts validated domain records into the representation expected by the database loader.

### Database

Owns connection management, SQLAlchemy models, audit logging, and persistence.

## 4. PostgreSQL Model

The current database uses a dimensional/event-oriented relational design.

### Dimensions

- `dim_team`
- `dim_team_alias`
- `dim_player`
- `dim_venue`
- `dim_match`

### Relationship / event tables

- `match_team`
- `match_innings`
- `fact_delivery`
- `delivery_extras`
- `delivery_wickets`

### ETL operational tables

- `etl_run`
- `etl_file_log`
- `etl_file_quality_issue`

## 5. Important Design Decisions

### Delivery-level storage

Each delivery is stored as an event so downstream analytics and ML feature generation can operate at ball level.

### Delivery sequence

The database uses `over_number + delivery_sequence` for delivery-position uniqueness.

This avoids treating `over_number + ball_number` as globally unique because illegal deliveries such as wides/no-balls can make the source ball numbering unsuitable as a database uniqueness key.

### Team aliases

Historical team names are normalized through `dim_team_alias` rather than creating separate analytical teams for renamed franchises.

### DQ audit separation

Data-quality findings are stored separately from the core cricket facts. This keeps operational quality information available without polluting analytical tables.

## 6. Idempotency

The loader is designed to be safely rerunnable.

A rerun of an already loaded match does not create duplicate business rows.

This is important for production ETL because retries are normal when processing files.

## 7. Reconciliation Gate

The full dataset was reconciled from source counts to database counts.

A downstream analytics or ML sprint should use reconciliation results as a gate before treating the database as trusted analytical input.

## 8. Future Architecture

The following layers will be added only when implemented:

```text
PostgreSQL
   |
   +--> Analytics / SQL views
   |
   +--> Feature engineering
   |
   +--> ML model
   |
   +--> Structured GenAI tools
   |
   +--> RAG knowledge store
   |
   v
API
   |
   v
UI
```

No vector database or LLM layer is introduced merely because it is available; each future component must have a clear requirement.
