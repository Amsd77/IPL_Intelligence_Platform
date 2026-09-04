from dataclasses import dataclass
from datetime import date

from src.ingestion.parser import (
    DeliveryRecord,
    ExtraRecord,
    InningsRecord,
    MatchRecord,
    PlayerRecord,
    TeamRecord,
    VenueRecord,
)

@dataclass(frozen=True)
class TransformedTeam:
    team_name: str


@dataclass(frozen=True)
class TransformedPlayer:
    player_name: str
    registry_id: str | None


@dataclass(frozen=True)
class TransformedVenue:
    venue_name: str
    city: str | None


@dataclass(frozen=True)
class TransformedMatch:
    match_id: int
    season: str
    match_date: date

    toss_winner: str | None
    toss_decision: str | None

    winner: str | None

    match_type: str | None
    gender: str | None

    player_of_match: tuple[str, ...]


@dataclass(frozen=True)
class TransformedDelivery:
    over_number: int
    delivery_sequence: int
    actual_delivery: str

    batter: str
    bowler: str
    non_striker: str

    batter_runs: int
    total_runs: int

    extras: tuple[ExtraRecord, ...]
    wickets: tuple
    
def _transform_deliveries(
    deliveries: tuple[DeliveryRecord, ...],
) -> tuple[TransformedDelivery, ...]:
    """Transform delivery records into database-ready structures."""

    transformed: list[TransformedDelivery] = []

    for sequence, delivery in enumerate(
        deliveries,
        start=1,
    ):
        transformed.append(
            TransformedDelivery(
                over_number=delivery.over_number,
                delivery_sequence=sequence,
                actual_delivery=delivery.actual_delivery,
                batter=delivery.batter,
                bowler=delivery.bowler,
                non_striker=delivery.non_striker,
                batter_runs=delivery.batter_runs,
                total_runs=delivery.total_runs,
                extras=delivery.extras,
                wickets=delivery.wickets,
            )
        )

    return tuple(transformed)

@dataclass(frozen=True)
class TransformedInnings:
    innings_number: int
    batting_team: str
    deliveries: tuple[TransformedDelivery, ...]
    
def _transform_innings(
    innings: tuple[InningsRecord, ...],
) -> tuple[TransformedInnings, ...]:
    """Transform innings records."""

    transformed: list[TransformedInnings] = []

    for innings_record in innings:

        transformed.append(
            TransformedInnings(
                innings_number=innings_record.innings_number,
                batting_team=innings_record.batting_team,
                deliveries=_transform_deliveries(
                    innings_record.deliveries
                ),
            )
        )

    return tuple(transformed)

def _transform_teams(
    teams: tuple[TeamRecord, ...],
) -> tuple[TransformedTeam, ...]:
    """Transform team records."""

    return tuple(
        TransformedTeam(
            team_name=team.name.strip()
        )
        for team in teams
    )
    
def _transform_players(
    players: tuple[PlayerRecord, ...],
) -> tuple[TransformedPlayer, ...]:
    """Transform player records."""

    return tuple(
        TransformedPlayer(
            player_name=player.name.strip(),
            registry_id=player.registry_id,
        )
        for player in players
    )
    
def _transform_venue(
    venue: VenueRecord | None,
) -> TransformedVenue | None:
    """Transform venue information."""

    if venue is None:
        return None

    return TransformedVenue(
        venue_name=venue.name.strip(),
        city=venue.city.strip()
        if venue.city
        else None,
    )
    
def _transform_match(
    match: MatchRecord,
) -> TransformedMatch:
    """Transform match-level information."""

    return TransformedMatch(
        match_id=match.match_id,
        season=match.season,
        match_date=match.match_date,
        toss_winner=match.toss_winner,
        toss_decision=match.toss_decision,
        winner=match.winner,
        match_type=match.match_type,
        gender=match.gender,
        player_of_match=match.player_of_match,
    )
    
@dataclass(frozen=True)
class TransformedMatchPackage:
    match: TransformedMatch
    teams: tuple[TransformedTeam, ...]
    players: tuple[TransformedPlayer, ...]
    venue: TransformedVenue | None
    innings: tuple[TransformedInnings, ...]
    
def transform_match(
    match: MatchRecord,
) -> TransformedMatchPackage:
    """
    Transform a validated MatchRecord into
    database-ready structures.

    No database access occurs here.
    """

    return TransformedMatchPackage(
        match=_transform_match(match),
        teams=_transform_teams(match.teams),
        players=_transform_players(match.players),
        venue=_transform_venue(match.venue),
        innings=_transform_innings(match.innings),
    )