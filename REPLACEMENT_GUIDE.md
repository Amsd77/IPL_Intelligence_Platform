# Updated Project Package

This package contains the updated engineering documentation and project tracker for the IPL Intelligence Platform.

## Recommended replacement

Replace your existing:

```text
docs/
project_tracker.xlsx
```

with the corresponding contents from this package.

Also copy:

```text
CONTRIBUTING.md
```

to the project root.

## Important

Do **not** replace your entire project root with this package.

Your existing `src/`, `data/`, `tests/`, `scripts/`, `.env`, database, and other implementation files are not included here because they are already working locally and should not be overwritten.

After copying the files, verify:

```powershell
git status
pytest -q
```

Then we can start the professional Git workflow from the next development task.
