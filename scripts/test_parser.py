from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"

def main() -> None:
    """Parse one real Cricsheet match."""

    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise RuntimeError(
            f"No JSON files found in {DATA_DIR}"
        )

    file_path = json_files[0]

    print("=" * 60)
    print("PARSER TEST")
    print("=" * 60)
    print(f"Source file: {file_path.name}")

    data = read_json(file_path)

    # match = parse_match(data)
    match_id = int(file_path.stem)

    match = parse_match(
        data=data,
        match_id=match_id,
    )
    
    print(f"Source file ID : {file_path.stem}")

    print("\nMATCH")
    print("-" * 60)
    print(f"Match ID       : {match.match_id}")
    print(f"Season         : {match.season}")
    print(f"Date           : {match.match_date}")
    print(f"Match type     : {match.match_type}")
    print(f"Gender         : {match.gender}")

    print("\nTEAMS")
    print("-" * 60)

    for team in match.teams:
        print(f"- {team.name}")

    print("\nVENUE")
    print("-" * 60)

    if match.venue:
        print(f"Name : {match.venue.name}")
        print(f"City : {match.venue.city}")
    else:
        print("No venue")

    print("\nTOSS")
    print("-" * 60)
    print(f"Winner   : {match.toss_winner}")
    print(f"Decision : {match.toss_decision}")

    print("\nRESULT")
    print("-" * 60)
    print(f"Winner          : {match.winner}")
    print(f"Player of match : {match.player_of_match}")

    print("\nPLAYERS")
    print("-" * 60)
    print(f"Players found: {len(match.players)}")

    for player in match.players[:10]:
        print(
            f"- {player.name} "
            f"(registry_id={player.registry_id})"
        )

    print("\nINNINGS")
    print("-" * 60)

    for innings in match.innings:

        print(
            f"Innings {innings.innings_number}: "
            f"{innings.batting_team}"
        )

        print(
            f"  Deliveries: {len(innings.deliveries)}"
        )

    total_deliveries = sum(
        len(innings.deliveries)
        for innings in match.innings
    )

    total_extras = sum(
        len(delivery.extras)
        for innings in match.innings
        for delivery in innings.deliveries
    )

    total_wickets = sum(
        len(delivery.wickets)
        for innings in match.innings
        for delivery in innings.deliveries
    )

    print("\nTOTALS")
    print("-" * 60)
    print(f"Innings    : {len(match.innings)}")
    print(f"Deliveries : {total_deliveries}")
    print(f"Extras     : {total_extras}")
    print(f"Wickets    : {total_wickets}")


if __name__ == "__main__":
    main()