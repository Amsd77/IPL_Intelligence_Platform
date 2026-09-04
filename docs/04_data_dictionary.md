# 04 Data Dictionary

This document describes the current PostgreSQL analytical model.

## Core Tables

### `dim_team`

| Column | Meaning |
|---|---|
| `team_id` | Surrogate team identifier |
| `team_name` | Canonical team name |

### `dim_team_alias`

| Column | Meaning |
|---|---|
| `team_alias_id` | Alias identifier |
| `team_id` | Canonical team reference |
| `raw_team_name` | Historical/source team name |

### `dim_player`

| Column | Meaning |
|---|---|
| `player_id` | Player identifier |
| `player_name` | Player name |
| `registry_id` | Cricsheet registry identifier when available |

### `dim_venue`

| Column | Meaning |
|---|---|
| `venue_id` | Venue identifier |
| `venue_name` | Venue name |
| `city` | Venue city |

### `dim_match`

| Column | Meaning |
|---|---|
| `match_id` | Source match identifier |
| `season` | IPL season |
| `match_date` | Match date |
| `venue_id` | Venue reference |
| `city` | Match city |
| `toss_winner_id` | Toss-winning team |
| `toss_decision` | Toss decision |
| `winner_id` | Match winner |
| `match_type` | Match type |
| `gender` | Match gender |
| `player_of_match` | Player-of-match value from source |

### `match_team`

Associates a match with its participating teams.

### `match_innings`

Represents an innings within a match.

| Column | Meaning |
|---|---|
| `innings_id` | Surrogate innings identifier |
| `match_id` | Match reference |
| `innings_number` | Source innings order |
| `batting_team_id` | Batting team |

### `fact_delivery`

The central event/fact table.

| Column | Meaning |
|---|---|
| `delivery_id` | Delivery identifier |
| `innings_id` | Innings reference |
| `over_number` | Over number |
| `delivery_sequence` | Stored delivery sequence within the over |
| `actual_delivery` | Source delivery label/value |
| `batter_id` | Batter |
| `bowler_id` | Bowler |
| `non_striker_id` | Non-striker |
| `batter_runs` | Runs credited to batter |
| `total_runs` | Total runs from delivery |

### `delivery_extras`

Stores delivery-level extras.

| Column | Meaning |
|---|---|
| `delivery_extra_id` | Extra-row identifier |
| `delivery_id` | Delivery reference |
| `extra_type` | Extra category |
| `runs` | Extra runs |

### `delivery_wickets`

Stores delivery-level wickets.

| Column | Meaning |
|---|---|
| `delivery_wicket_id` | Wicket-row identifier |
| `delivery_id` | Delivery reference |
| `player_out_id` | Dismissed player |
| `kind` | Dismissal kind |

## ETL Audit Tables

### `etl_run`

Tracks one execution of the ingestion pipeline.

### `etl_file_log`

Tracks processing status for an individual source file, including stage and timing information.

### `etl_file_quality_issue`

Stores persisted data-quality findings.

| Column | Meaning |
|---|---|
| `quality_issue_id` | Issue identifier |
| `file_log_id` | Source-file audit reference |
| `rule_id` | DQ rule identifier |
| `field` | Affected field |
| `message` | Human-readable issue |
| `severity` | `ERROR` or `WARNING` |
| `created_at` | Issue creation timestamp |

## Key Relationships

```text
dim_team
   |
   +--> dim_team_alias
   |
   +--> dim_match
          |
          +--> match_team
          |
          +--> match_innings
                 |
                 +--> fact_delivery
                        |
                        +--> delivery_extras
                        |
                        +--> delivery_wickets
```

## Source-to-Database Reconciliation

Current verified counts:

| Entity | Source | Database |
|---|---:|---:|
| Matches | 1,243 | 1,243 |
| Innings | 2,514 | 2,514 |
| Deliveries | 295,732 | 295,732 |
| Extras | 16,255 | 16,255 |
| Wickets | 14,705 | 14,705 |
