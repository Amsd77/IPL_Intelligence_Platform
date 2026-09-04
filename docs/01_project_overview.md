# IPL Intelligence Platform — Project Overview

## 1. Purpose

The IPL Intelligence Platform is an end-to-end cricket analytics and AI project built from IPL match data.

The project is being developed as a production-style learning project with clear separation between data engineering, analytics, machine learning, GenAI, RAG, API, and presentation layers.

## 2. Current Scope

The planned platform will eventually cover:

- IPL match and delivery-level analytics
- Player analytics
- Team analytics
- Venue analytics
- IPL win prediction
- GenAI-powered cricket interaction
- RAG-based cricket knowledge retrieval
- API layer
- User-facing application
- Testing and deployment

## 3. Current Development Stage

Current stage: **Foundation / Data Engineering — ingestion and data-quality foundation completed**

Completed:

- Project structure and Conda environment
- Python 3.12.13
- Cricsheet IPL JSON source inspection
- PostgreSQL 17.6 and Python database connectivity
- SQLAlchemy database models
- Relational database schema and ETL audit tables
- JSON reader and match parser
- Structural match validation
- Data-quality framework with blocking errors and non-blocking warnings
- Transformation and database loading
- ETL run/file audit logging
- Full IPL source ingestion
- Source integrity verification
- Source-to-database reconciliation
- Idempotency verification
- Data-quality issue persistence and audit verification
- Full regression test suite

### Current verified dataset load

- Source JSON files: **1,243**
- Matches: **1,243**
- Innings: **2,514**
- Deliveries: **295,732**
- Extras: **16,255**
- Wickets: **14,705**
- Full ingestion run: **1,243/1,243 successful**
- Processing failures: **0**
- Reconciliation: **PASS**
- Idempotency check: **PASS**

## 4. Core Design Principle

The project follows:

**Inspect → Design → Implement → Test → Review → Document**

We do not design the production pipeline from assumptions about the source data. The raw dataset is profiled first, and implementation decisions are documented.

## 5. Source Data

The current source is Cricsheet IPL match JSON data.

Raw source files are preserved under:

```text
data/raw/cricsheet/
```

Raw data should not be manually modified.

Historical team-name variations are normalized through a team-alias mapping layer.

## 6. High-Level Architecture

```text
Cricsheet JSON
      |
      v
JSON Reader
      |
      v
Match Parser
      |
      v
Structural Validation
      |
      v
Data Quality Checks
      |
      +------> DQ audit issues
      |
      v
Transformation
      |
      v
PostgreSQL
      |
      +----> Analytics
      |
      +----> ML Features / Models
      |
      +----> Structured context for GenAI
      |
      +----> RAG / Knowledge layer
      |
      v
API / Application
```

## 7. Database Design Summary

The relational model separates dimensions, match/innings relationships, and delivery-level facts.

Core entities include:

- `dim_team`
- `dim_team_alias`
- `dim_player`
- `dim_venue`
- `dim_match`
- `match_team`
- `match_innings`
- `fact_delivery`
- `delivery_extras`
- `delivery_wickets`

Operational/audit entities include:

- `etl_run`
- `etl_file_log`
- `etl_file_quality_issue`

## 8. Current Quality Policy

Data-quality rules are divided into:

- **ERROR** — blocks loading of the affected file
- **WARNING** — does not block loading, but is persisted for audit

Current warning findings from the full validation analysis:

- DQ010 — missing venue city: 51
- DQ011 — missing player of match: 9
- Total warnings: 60
- Blocking DQ errors: 0

## 9. Intended Users

The platform is being designed for:

- Data analysts
- Cricket analysts
- Developers
- AI/ML users
- End users asking cricket-related questions

## 10. Documentation Philosophy

Every major implementation should document:

1. What was built
2. Why the approach was selected
3. How it works
4. How it is tested
5. Failure cases
6. Known limitations
7. Important engineering decisions

Documentation is maintained alongside implementation so another developer can understand and continue the project.
