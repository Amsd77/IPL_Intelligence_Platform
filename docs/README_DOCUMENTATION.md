# Documentation Guide

This folder contains the engineering documentation for the IPL Intelligence Platform.

## Documentation Structure

```text
docs/
├── 01_project_overview.md
├── 02_architecture.md
├── 03_environment_setup.md
├── 04_data_dictionary.md
├── 05_database_design.md
├── 06_etl_pipeline.md
├── 07_ml_model.md
├── 08_genai.md
├── 09_rag.md
├── 10_api.md
├── 11_deployment.md
├── 12_testing.md
├── 13_troubleshooting.md
├── 14_change_log.md
└── 15_data_quality.md
```

Future documents are added only when the corresponding part of the system is actually implemented.

## Documentation Rule

For each major feature, record:

- What
- Why
- How
- Tests
- Failure cases
- Known limitations
- Important decisions

## Project Tracking Rule

At the end of each meaningful sprint/feature:

1. Update the relevant Markdown documentation.
2. Update the Excel project tracker.
3. Add important architecture decisions.
4. Run tests and verification.
5. Create a logical Git commit.
6. Push the branch and use a Pull Request workflow for changes intended for `main`.

This is intentionally modeled after a professional team workflow even though the project currently has one developer.

## Source of Truth

Code and database state are the implementation source of truth.

Documentation explains the implementation.

The Excel tracker records project progress and decisions at task level.

Git records the history of code/documentation changes.
