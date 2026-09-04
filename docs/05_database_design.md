# 05 Database Design

## 1. Design Objective

The database is designed to preserve detailed cricket events while keeping dimensions and operational ETL metadata separate.

PostgreSQL was selected because the platform requires relational integrity, joins, constraints, repeatable analytical queries, and reliable persistence.

## 2. Model Structure

```text
Dimensions
  |
  +-- dim_team
  +-- dim_team_alias
  +-- dim_player
  +-- dim_venue
  +-- dim_match
          |
          v
Relationships
  +-- match_team
  +-- match_innings
          |
          v
Fact/Event
  +-- fact_delivery
          |
          +-- delivery_extras
          +-- delivery_wickets
```

## 3. Integrity Constraints

Examples of implemented constraints include:

- Primary keys on all core entities
- Foreign keys between facts and dimensions
- Unique team names
- Unique raw team aliases
- Unique venue name/city combination
- Unique match/innings number
- Unique delivery position using `innings_id`, `over_number`, and `delivery_sequence`

## 4. Why Delivery-Level Facts

Ball-by-ball data is the most detailed reusable analytical layer in this project.

From delivery facts we can later derive:

- batter runs
- bowling outcomes
- boundaries
- wickets
- extras
- strike rate
- economy
- innings totals
- powerplay/death-over metrics
- model features

Aggregated tables can be derived later without losing event detail.

## 5. Why Separate ETL Audit Tables

Analytical cricket tables answer cricket questions.

ETL audit tables answer operational questions such as:

- Which run processed this file?
- Did the file succeed?
- At which stage did it fail?
- How long did it take?
- Which DQ rules fired?

Keeping these concerns separate improves maintainability and debugging.

## 6. Idempotency

The loader uses database uniqueness and lookup behavior so a retry of an already processed match does not duplicate its business rows.

Idempotency was explicitly verified using match `1082591`.

## 7. Data Quality Audit

`etl_file_quality_issue` stores quality findings linked to `etl_file_log`.

This creates the audit relationship:

```text
etl_run
   |
   v
etl_file_log
   |
   v
etl_file_quality_issue
```

## 8. Known Limitations

The current schema is optimized for the present IPL analytics foundation.

Future sprints may introduce additional tables or views for:

- derived player statistics
- team performance aggregates
- feature-store-like datasets
- model predictions
- API-specific read models

Those should be added only when supported by a concrete downstream requirement.
