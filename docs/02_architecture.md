# 02 Architecture

## 1. Architecture Goal

The platform is designed as a layered system where each responsibility is isolated.

The current implementation covers the data-engineering foundation and the first Analytics Foundation layer. ML, GenAI, RAG, API, UI, and deployment remain downstream layers.

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

### Analytics

Provides SQL-backed analytical functions over the trusted PostgreSQL data. Current modules cover player batting, player bowling, team batting, team bowling, match summaries, and match innings statistics.

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

## 5. Analytics Layer

Analytics functions query PostgreSQL through SQLAlchemy sessions rather than duplicating business facts in application memory. Match-level analytics are built from the normalized match, innings, team, delivery, extra, and wicket tables.

### Separate delivery and wicket aggregation

Match innings statistics use separate aggregation paths for delivery statistics and wicket statistics. Joining `fact_delivery` directly to `delivery_wickets` can multiply delivery rows when a delivery contains multiple wicket records, which can inflate run and delivery counts. Separate CTEs avoid this row-multiplication problem while allowing each metric to use the appropriate grain.

### Legal delivery semantics

For innings analytics, legal deliveries exclude deliveries containing `wides` or `noballs`. Total delivery records and legal deliveries are therefore tracked separately.

### Wicket-lost semantics

Innings wickets lost exclude `retired hurt`, because that event does not represent a dismissal/wicket lost in scorecard-style innings analytics.

## 6. Important Design Decisions

### Delivery-level storage

Each delivery is stored as an event so downstream analytics and ML feature generation can operate at ball level.

### Delivery sequence

The database uses `over_number + delivery_sequence` for delivery-position uniqueness.

This avoids treating `over_number + ball_number` as globally unique because illegal deliveries such as wides/no-balls can make the source ball numbering unsuitable as a database uniqueness key.

### Team aliases

Historical team names are normalized through `dim_team_alias` rather than creating separate analytical teams for renamed franchises.

### DQ audit separation

Data-quality findings are stored separately from the core cricket facts. This keeps operational quality information available without polluting analytical tables.

## 7. Idempotency

The loader is designed to be safely rerunnable.

A rerun of an already loaded match does not create duplicate business rows.

This is important for production ETL because retries are normal when processing files.

## 8. Reconciliation Gate

The full dataset was reconciled from source counts to database counts.

A downstream analytics or ML sprint should use reconciliation results as a gate before treating the database as trusted analytical input.

## 9. Future Architecture

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
