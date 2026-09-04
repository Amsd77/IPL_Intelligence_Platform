from src.database.connection import engine
from src.database.models import Base


def create_tables() -> None:
    """Create all application tables in PostgreSQL."""

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()