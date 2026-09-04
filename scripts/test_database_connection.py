from sqlalchemy import text

from src.database.connection import engine


def test_connection() -> None:
    """Verify that the application can connect to PostgreSQL."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    if value != 1:
        raise RuntimeError("Database connection test failed.")

    print("Database connection successful.")


if __name__ == "__main__":
    test_connection()