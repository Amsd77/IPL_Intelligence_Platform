from sqlalchemy import text

from src.database.connection import engine


def main() -> None:
    statements = [
        """
        ALTER TABLE dim_match
        ADD COLUMN IF NOT EXISTS outcome_result VARCHAR(30)
        """,
        """
        ALTER TABLE dim_match
        ADD COLUMN IF NOT EXISTS outcome_deciding_team_id INTEGER
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'fk_dim_match_outcome_deciding_team'
            ) THEN
                ALTER TABLE dim_match
                ADD CONSTRAINT fk_dim_match_outcome_deciding_team
                FOREIGN KEY (outcome_deciding_team_id)
                REFERENCES dim_team(team_id);
            END IF;
        END
        $$;
        """,
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("Match outcome migration completed successfully.")


if __name__ == "__main__":
    main()