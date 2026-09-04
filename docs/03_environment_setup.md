# Environment Setup

## Current Environment

| Component | Current Value |
|---|---|
| Operating system | Windows |
| Python | 3.12.13 |
| Conda environment | `IPL_Intelligence_Platform` |
| PostgreSQL | 17.6 |
| Database | `ipl_intelligence` |
| Database user | `postgres` |

## Python Environment

The project uses an isolated Conda environment:

```text
IPL_Intelligence_Platform
```

Python executable verified at:

```text
C:\Users\abhay\anaconda3\envs\IPL_Intelligence_Platform\python.exe
```

## Core Dependencies

Current dependencies include:

```text
pandas
sqlalchemy
psycopg2-binary
pydantic
python-dotenv
pytest
```

Install with:

```powershell
python -m pip install -r requirements.txt
```

## PostgreSQL

PostgreSQL 17.6 is installed locally and the service is running.

The PostgreSQL client can be invoked directly when it is not available through PATH:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

## Database

The project uses:

```text
ipl_intelligence
```

## Environment Variables

Local secrets/configuration are stored in `.env`.

Expected template:

```text
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/ipl_intelligence
```

Never commit the real `.env` file or database password to source control.

`.env.example` contains only the configuration template.

## Database Connection Layer

```text
python-dotenv
      |
      v
SQLAlchemy
      |
      v
psycopg2
      |
      v
PostgreSQL
```

Connection implementation:

```text
src/database/connection.py
```

## Connection Test

Run from the project root:

```powershell
python -m scripts.test_database_connection
```

Expected successful output:

```text
Database connection successful.
```

## Test Suite

Run:

```powershell
pytest -q
```

The current full regression suite has passed after the ingestion/data-quality implementation.

## Ingestion

Run the full ingestion module from the project root:

```powershell
python -m scripts.run_ingestion
```

## Important Practice

Always verify the active Python executable before installing dependencies:

```powershell
python -c "import sys; print(sys.executable)"
```

It should point to:

```text
anaconda3\envs\IPL_Intelligence_Platform\python.exe
```

## Git Safety

Before committing:

```powershell
git status
git diff
pytest -q
```

Never commit:

- `.env`
- passwords
- database credentials
- generated secrets
- local virtual environments
