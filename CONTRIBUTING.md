# Contributing / Git Workflow

This project is a solo development project, but the workflow intentionally simulates a professional team environment.

## 1. Branch Strategy

Keep `main` stable.

Create a branch for each logical unit of work:

```text
feature/<short-name>
fix/<short-name>
refactor/<short-name>
docs/<short-name>
test/<short-name>
```

Examples:

```text
feature/data-quality-framework
feature/analytics-data-model
fix/delivery-sequence-constraint
docs/update-etl-documentation
```

## 2. Work Cycle

```text
main
  |
  +--> create feature branch
          |
          +--> implement
          +--> test
          +--> review diff
          +--> commit
          +--> push
          +--> Pull Request
          +--> merge to main
```

## 3. When to Commit

Do **not** commit every single line or tiny experiment.

Commit after a logical, working unit is complete.

Good examples:

```text
feat: add data quality result model
feat: persist file quality issues
test: add negative data quality cases
feat: add idempotent match loader
docs: document ETL architecture
chore: update project tracker
```

A feature can have multiple commits while being developed. The important rule is that each commit should be understandable and reviewable.

## 4. Before Every Commit

Run:

```powershell
git status
git diff
pytest -q
```

For ETL changes, also run the relevant ingestion/reconciliation checks.

Then stage intentionally:

```powershell
git add <files>
```

Review the staged diff:

```powershell
git diff --cached
```

Commit:

```powershell
git commit -m "feat: add data quality audit persistence"
```

## 5. Pull Request Simulation as a Solo Developer

Even with one developer, use Pull Requests when a logical feature is complete.

Example:

```text
feature/data-quality-framework
        |
        v
Pull Request -> main
```

PR checklist:

- implementation complete
- tests pass
- documentation updated
- tracker updated
- architecture decisions recorded
- no secrets committed
- diff reviewed
- known limitations recorded

This gives practical experience with the same workflow used by multi-developer teams.

## 6. Commit Size

Prefer:

```text
small + logical + working
```

Avoid:

```text
one giant commit containing unrelated features
```

For example, these are better separated:

```text
feat: add DQ rule engine
test: add DQ negative tests
feat: persist DQ issues
docs: document data quality
chore: update tracker
```

## 7. Never Commit

Never commit:

```text
.env
passwords
API keys
database credentials
local virtual environments
large generated artifacts
```

Check `.gitignore` before the first push.

## 8. Professional Rule for This Project

At every major project level, we will explicitly decide:

1. What was completed?
2. What tests passed?
3. What documentation changed?
4. What tracker rows changed?
5. What architecture decisions changed?
6. What commit(s) should represent the work?
7. Whether the branch is ready for a Pull Request.

The assistant will tell you the recommended commit message instead of making you guess.

## 9. Important Distinction

Git commit = records a logical change.

Pull Request = requests review/integration.

Merge = integrates the reviewed branch into `main`.

These are different steps in a professional workflow.
