from sqlalchemy.orm import Session

from src.analytics.team_head_to_head import (
    get_team_head_to_head,
    get_team_head_to_head_by_season,
)
from src.database.connection import engine


def main() -> None:
    with Session(engine) as session:

        print("=" * 60)
        print("TEAM HEAD-TO-HEAD")
        print("=" * 60)

        result = get_team_head_to_head(
            session,
            team_a_id=9,
            team_b_id=4,
        )

        print(result)

        print()
        print("=" * 60)
        print("TEAM HEAD-TO-HEAD BY SEASON")
        print("=" * 60)

        seasonal_result = get_team_head_to_head_by_season(
            session,
            team_a_id=9,
            team_b_id=4,
        )

        for row in seasonal_result:
            print(row)


if __name__ == "__main__":
    main()