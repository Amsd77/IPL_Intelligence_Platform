from sqlalchemy.orm import Session

from src.database.connection import engine
from src.analytics.player_batting import get_top_batters


def main() -> None:
    print("=" * 70)
    print("IPL PLAYER BATTING ANALYTICS")
    print("=" * 70)

    with Session(engine) as session:

        players = get_top_batters(
            session=session,
            limit=20,
        )

    print(
        f"{'Player':<20}"
        f"{'Matches':>8}"
        f"{'Innings':>9}"
        f"{'Runs':>8}"
        f"{'Balls':>8}"
        f"{'Dismiss':>9}"
        f"{'Avg':>9}"
        f"{'SR':>9}"
    )

    print("-" * 80)

    for player in players:

        print(
            f"{player['player_name']:<20}"
            f"{player['matches']:>8}"
            f"{player['innings']:>9}"
            f"{player['runs']:>8}"
            f"{player['balls_faced']:>8}"
            f"{player['dismissals']:>9}"
            f"{str(player['batting_average']):>9}"
            f"{str(player['strike_rate']):>9}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()