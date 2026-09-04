from dataclasses import dataclass, field
from datetime import date
from typing import Any


# ============================================================
# Parsed data models
# ============================================================


@dataclass(frozen=True)
class TeamRecord:
    """Canonical/raw team information found in a match."""

    name: str


@dataclass(frozen=True)
class PlayerRecord:
    """Player information found in a match."""

    name: str
    registry_id: str | None = None


@dataclass(frozen=True)
class VenueRecord:
    """Venue information for a match."""

    name: str
    city: str | None = None


@dataclass(frozen=True)
class ExtraRecord:
    """Extra runs associated with a delivery."""

    extra_type: str
    runs: int


@dataclass(frozen=True)
class WicketRecord:
    """Wicket information associated with a delivery."""

    player_out: str
    kind: str


# @dataclass(frozen=True)
# class DeliveryRecord:
#     """A single ball-by-ball delivery."""

#     over_number: int
#     ball_number: int

#     batter: str
#     bowler: str
#     non_striker: str

#     batter_runs: int
#     total_runs: int

#     extras: tuple[ExtraRecord, ...] = field(default_factory=tuple)
#     wickets: tuple[WicketRecord, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class DeliveryRecord:
    """A single ball-by-ball delivery."""

    over_number: int
    ball_number: int
    actual_delivery: str

    batter: str
    bowler: str
    non_striker: str

    batter_runs: int
    total_runs: int

    extras: tuple[ExtraRecord, ...] = field(default_factory=tuple)
    wickets: tuple[WicketRecord, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InningsRecord:
    """One innings within a match."""

    innings_number: int
    batting_team: str
    deliveries: tuple[DeliveryRecord, ...]


@dataclass(frozen=True)
class MatchRecord:
    """Parsed representation of one Cricsheet match."""

    match_id: int
    season: str
    match_date: date

    teams: tuple[TeamRecord, ...]

    venue: VenueRecord | None

    toss_winner: str | None
    toss_decision: str | None

    winner: str | None

    match_type: str | None
    gender: str | None

    player_of_match: tuple[str, ...]

    players: tuple[PlayerRecord, ...]

    innings: tuple[InningsRecord, ...]

def _parse_players(
    info: dict[str, Any],
) -> tuple[PlayerRecord, ...]:
    """Parse players and their Cricsheet registry IDs."""

    players: list[PlayerRecord] = []

    raw_players = info.get("players", {})
    registry = info.get("registry", {})

    if not isinstance(raw_players, dict):
        return tuple()

    if not isinstance(registry, dict):
        registry = {}

    people_registry = registry.get("people", {})

    if not isinstance(people_registry, dict):
        people_registry = {}

    for team_players in raw_players.values():

        if not isinstance(team_players, list):
            continue

        for player_name in team_players:

            if not isinstance(player_name, str):
                continue

            registry_id = people_registry.get(player_name)

            players.append(
                PlayerRecord(
                    name=player_name,
                    registry_id=(
                        str(registry_id)
                        if registry_id
                        else None
                    ),
                )
            )

    return tuple(players)

def _parse_venue(info: dict[str, Any]) -> VenueRecord | None:
    """Parse venue and city information."""

    venue = info.get("venue")
    city = info.get("city")

    if not venue:
        return None

    return VenueRecord(
        name=str(venue),
        city=str(city) if city else None,
    )
    
def _parse_toss(info: dict[str, Any]) -> tuple[str | None, str | None]:
    """Parse toss winner and decision."""

    toss = info.get("toss", {})

    if not isinstance(toss, dict):
        return None, None

    winner = toss.get("winner")
    decision = toss.get("decision")

    return (
        str(winner) if winner else None,
        str(decision) if decision else None,
    )
    
def _parse_winner(info: dict[str, Any]) -> str | None:
    """Extract the match winner when available."""

    outcome = info.get("outcome", {})

    if not isinstance(outcome, dict):
        return None

    winner = outcome.get("winner")

    if winner:
        return str(winner)

    return None

def _parse_extras(raw_extras: Any) -> tuple[ExtraRecord, ...]:
    """Parse delivery extras."""

    if not isinstance(raw_extras, dict):
        return tuple()

    extras: list[ExtraRecord] = []

    for extra_type, runs in raw_extras.items():

        try:
            runs_value = int(runs)
        except (TypeError, ValueError):
            continue

        extras.append(
            ExtraRecord(
                extra_type=str(extra_type),
                runs=runs_value,
            )
        )

    return tuple(extras)

def _parse_wickets(raw_wickets: Any) -> tuple[WicketRecord, ...]:
    """Parse wickets associated with a delivery."""

    if not isinstance(raw_wickets, list):
        return tuple()

    wickets: list[WicketRecord] = []

    for wicket in raw_wickets:

        if not isinstance(wicket, dict):
            continue

        player_out = wicket.get("player_out")
        kind = wicket.get("kind")

        if not player_out or not kind:
            continue

        wickets.append(
            WicketRecord(
                player_out=str(player_out),
                kind=str(kind),
            )
        )

    return tuple(wickets)

def _parse_delivery(
    delivery: dict[str, Any],
    over_number: int,
) -> DeliveryRecord:
    """Parse one Cricsheet delivery."""

    batter = delivery.get("batter")
    bowler = delivery.get("bowler")
    non_striker = delivery.get("non_striker")

    if not batter or not bowler or not non_striker:
        raise ValueError(
            "Delivery is missing batter, bowler, or non-striker."
        )

    actual_delivery = delivery.get("actual_delivery")

    if actual_delivery is None:
        raise ValueError(
            "Delivery is missing 'actual_delivery'."
        )

    try:
        ball_number = int(
            str(actual_delivery).split(".")[1]
        )
    except (IndexError, ValueError):
        raise ValueError(
            f"Invalid actual_delivery value: {actual_delivery}"
        )

    runs = delivery.get("runs", {})

    if not isinstance(runs, dict):
        runs = {}

    batter_runs = int(runs.get("batter", 0))
    total_runs = int(runs.get("total", 0))

    extras = _parse_extras(
        delivery.get("extras")
    )

    wickets = _parse_wickets(
        delivery.get("wickets")
    )

    return DeliveryRecord(
        over_number=over_number,
        ball_number=ball_number,
        actual_delivery=str(actual_delivery),
        batter=str(batter),
        bowler=str(bowler),
        non_striker=str(non_striker),
        batter_runs=batter_runs,
        total_runs=total_runs,
        extras=extras,
        wickets=wickets,
    )
    
    
def _parse_innings(
    raw_innings: list[dict[str, Any]],
) -> tuple[InningsRecord, ...]:
    """Parse all innings from a match."""

    innings_records: list[InningsRecord] = []

    for innings_number, innings in enumerate(raw_innings, start=1):

        if not isinstance(innings, dict):
            continue

        batting_team = innings.get("team")

        if not batting_team:
            continue

        deliveries: list[DeliveryRecord] = []

        overs = innings.get("overs", [])

        if not isinstance(overs, list):
            continue

        for over in overs:

            if not isinstance(over, dict):
                continue

            over_number = int(over.get("over", 0))

            raw_deliveries = over.get("deliveries", [])

            if not isinstance(raw_deliveries, list):
                continue

            for delivery in raw_deliveries:

                if not isinstance(delivery, dict):
                    continue

                deliveries.append(
                    _parse_delivery(
                        delivery=delivery,
                        over_number=over_number,
                    )
                )

        innings_records.append(
            InningsRecord(
                innings_number=innings_number,
                batting_team=str(batting_team),
                deliveries=tuple(deliveries),
            )
        )

    return tuple(innings_records)

# def parse_match(data: dict[str, Any]) -> MatchRecord:
def parse_match(data: dict[str, Any],match_id: int,) -> MatchRecord:
    """
    Parse one Cricsheet match dictionary into a MatchRecord.
    """

    info = data.get("info")

    if not isinstance(info, dict):
        raise ValueError("Match data does not contain valid 'info'.")

    meta = data.get("meta", {})

    if not isinstance(meta, dict):
        meta = {}

    # --------------------------------------------------------
    # Match ID
    # --------------------------------------------------------

    # raw_match_id = info.get("registry", {}).get("data", {}).get("match_id")

    # if raw_match_id is None:
    #     raw_match_id = info.get("match_id")

    # if raw_match_id is None:
    #     raise ValueError(
    #         "Unable to determine match ID from source data."
    #     )

    # match_id = int(raw_match_id)

    # --------------------------------------------------------
    # Season
    # --------------------------------------------------------

    season = info.get("season")

    if season is None:
        raise ValueError("Match is missing season.")

    season = str(season)

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    dates = info.get("dates", [])

    if not dates:
        raise ValueError("Match is missing match date.")

    first_date = dates[0]

    match_date = date.fromisoformat(str(first_date))

    # --------------------------------------------------------
    # Teams
    # --------------------------------------------------------

    raw_teams = info.get("teams", [])

    if not isinstance(raw_teams, list):
        raw_teams = []

    teams = tuple(
        TeamRecord(name=str(team))
        for team in raw_teams
        if team
    )

    # --------------------------------------------------------
    # Venue
    # --------------------------------------------------------

    venue = _parse_venue(info)

    # --------------------------------------------------------
    # Toss
    # --------------------------------------------------------

    toss_winner, toss_decision = _parse_toss(info)

    # --------------------------------------------------------
    # Winner
    # --------------------------------------------------------

    winner = _parse_winner(info)

    # --------------------------------------------------------
    # Match type / gender
    # --------------------------------------------------------

    match_type = info.get("match_type")
    gender = info.get("gender")

    # --------------------------------------------------------
    # Player of the match
    # --------------------------------------------------------

    player_of_match = info.get("player_of_match", [])

    if isinstance(player_of_match, str):
        player_of_match = (player_of_match,)

    elif isinstance(player_of_match, list):
        player_of_match = tuple(
            str(player)
            for player in player_of_match
            if player
        )

    else:
        player_of_match = tuple()

    # --------------------------------------------------------
    # Players
    # --------------------------------------------------------

    players = _parse_players(info)

    # --------------------------------------------------------
    # Innings
    # --------------------------------------------------------

    raw_innings = data.get("innings", [])

    if not isinstance(raw_innings, list):
        raw_innings = []

    innings = _parse_innings(raw_innings)

    return MatchRecord(
        match_id=match_id,
        season=season,
        match_date=match_date,
        teams=teams,
        venue=venue,
        toss_winner=toss_winner,
        toss_decision=toss_decision,
        winner=winner,
        match_type=str(match_type) if match_type else None,
        gender=str(gender) if gender else None,
        player_of_match=player_of_match,
        players=players,
        innings=innings,
    )
    
