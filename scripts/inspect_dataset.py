from pathlib import Path
import json


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def load_match_file(file_path: Path) -> dict:
    """Load a single Cricsheet JSON match file."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# Main profiling function
# ---------------------------------------------------------

def inspect_dataset() -> None:
    """Inspect the structure of the Cricsheet dataset."""

    match_files = sorted(DATA_DIR.glob("*.json"))

    print("=" * 60)
    print("IPL DATASET PROFILE")
    print("=" * 60)

    print(f"\nData directory : {DATA_DIR}")
    print(f"Match files    : {len(match_files)}")

    if not match_files:
        print("\nERROR: No JSON files found.")
        return

    valid_matches = 0
    invalid_matches = 0

    total_innings = 0
    total_overs = 0
    total_deliveries = 0

    seasons = set()
    teams = set()
    venues = set()
    cities = set()

    for file_path in match_files:

        try:
            match = load_match_file(file_path)

        except json.JSONDecodeError:
            invalid_matches += 1
            print(f"Invalid JSON: {file_path.name}")
            continue

        valid_matches += 1

        info = match.get("info", {})

        # Match information
        season = info.get("season")

        if season is not None:
            seasons.add(str(season))

        for team in info.get("teams", []):
            teams.add(team)

        venue = info.get("venue")

        if venue:
            venues.add(venue)

        city = info.get("city")

        if city:
            cities.add(city)

        # Innings information
        innings_list = match.get("innings", [])

        total_innings += len(innings_list)

        for innings in innings_list:

            overs = innings.get("overs", [])

            total_overs += len(overs)

            for over in overs:

                deliveries = over.get("deliveries", [])

                total_deliveries += len(deliveries)

    print("\n" + "-" * 60)
    print("MATCH INFORMATION")
    print("-" * 60)

    print(f"Valid matches   : {valid_matches}")
    print(f"Invalid matches : {invalid_matches}")

    print("\n" + "-" * 60)
    print("DIMENSIONS")
    print("-" * 60)

    print(f"Seasons : {len(seasons)}")
    print(f"Teams   : {len(teams)}")
    print(f"Venues  : {len(venues)}")
    print(f"Cities  : {len(cities)}")

    print("\n" + "-" * 60)
    print("DELIVERY INFORMATION")
    print("-" * 60)

    print(f"Total innings    : {total_innings}")
    print(f"Total overs      : {total_overs}")
    print(f"Total deliveries : {total_deliveries}")

    print("\n" + "-" * 60)
    print("SEASONS")
    print("-" * 60)

    print(", ".join(sorted(seasons)))

    print("\n" + "-" * 60)
    print("TEAMS")
    print("-" * 60)

    for team in sorted(teams):
        print(f"- {team}")

    print("\n" + "=" * 60)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    inspect_dataset()