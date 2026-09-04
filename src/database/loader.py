from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.connection import engine
from src.database.models import (
    Team,
    Player,
    Venue,
    Match,
    MatchTeam,
    MatchInnings,
    Delivery,
    DeliveryExtra,
    DeliveryWicket,
)
from src.transformation.transformer import (
    TransformedMatchPackage,
)


def get_or_create_team(
    session: Session,
    team_name: str,
) -> int:
    """Return an existing team_id or create the team."""

    team = session.scalar(
        select(Team).where(
            Team.team_name == team_name
        )
    )

    if team is not None:
        return team.team_id

    team = Team(
        team_name=team_name
    )

    session.add(team)
    session.flush()

    return team.team_id


def get_or_create_player(
    session: Session,
    player_name: str,
    registry_id: str | None,
) -> int:
    """Return an existing player_id or create the player."""

    player = None

    if registry_id:
        player = session.scalar(
            select(Player).where(
                Player.registry_id == registry_id
            )
        )

    if player is None:
        player = session.scalar(
            select(Player).where(
                Player.player_name == player_name
            )
        )

    if player is not None:

        # If the existing player doesn't have a registry ID
        # but the source provides one, enrich the record.
        if (
            player.registry_id is None
            and registry_id is not None
        ):
            player.registry_id = registry_id
            session.flush()

        return player.player_id

    player = Player(
        player_name=player_name,
        registry_id=registry_id,
    )

    session.add(player)
    session.flush()

    return player.player_id


def get_or_create_venue(
    session: Session,
    venue_name: str,
    city: str | None,
) -> int:
    """Return an existing venue_id or create the venue."""

    venue = session.scalar(
        select(Venue).where(
            Venue.venue_name == venue_name,
            Venue.city == city,
        )
    )

    if venue is not None:
        return venue.venue_id

    venue = Venue(
        venue_name=venue_name,
        city=city,
    )

    session.add(venue)
    session.flush()

    return venue.venue_id


def build_reference_maps(
    session: Session,
    package: TransformedMatchPackage,
):
    """Create or retrieve reference entities."""

    team_map: dict[str, int] = {}

    for team in package.teams:

        team_map[team.team_name] = (
            get_or_create_team(
                session,
                team.team_name,
            )
        )

    player_map: dict[str, int] = {}

    for player in package.players:

        player_map[player.player_name] = (
            get_or_create_player(
                session,
                player.player_name,
                player.registry_id,
            )
        )

    venue_id = None

    if package.venue is not None:

        venue_id = get_or_create_venue(
            session,
            package.venue.venue_name,
            package.venue.city,
        )

    return (
        team_map,
        player_map,
        venue_id,
    )


def insert_match(
    session: Session,
    package: TransformedMatchPackage,
    team_map: dict[str, int],
    venue_id: int | None,
) -> None:
    """Insert match if it does not already exist."""

    existing = session.get(
        Match,
        package.match.match_id,
    )

    if existing is not None:
        return

    match = Match(
        match_id=package.match.match_id,
        season=package.match.season,
        match_date=package.match.match_date,
        venue_id=venue_id,
        city=(
            package.venue.city
            if package.venue is not None
            else None
        ),
        toss_winner_id=team_map.get(
            package.match.toss_winner
        ),
        toss_decision=package.match.toss_decision,
        winner_id=team_map.get(
            package.match.winner
        ),
        match_type=package.match.match_type,
        gender=package.match.gender,
        player_of_match=(
            ", ".join(
                package.match.player_of_match
            )
            if package.match.player_of_match
            else None
        ),
    )

    session.add(match)
    session.flush()


def insert_match_teams(
    session: Session,
    package: TransformedMatchPackage,
    team_map: dict[str, int],
) -> None:
    """Insert match-team relationships safely."""

    match_id = package.match.match_id

    for team in package.teams:

        team_id = team_map[team.team_name]

        existing = session.scalar(
            select(MatchTeam).where(
                MatchTeam.match_id == match_id,
                MatchTeam.team_id == team_id,
            )
        )

        if existing is not None:
            continue

        session.add(
            MatchTeam(
                match_id=match_id,
                team_id=team_id,
            )
        )

    session.flush()


def insert_innings(
    session: Session,
    package: TransformedMatchPackage,
    team_map: dict[str, int],
) -> dict[int, int]:
    """Insert innings and return innings IDs."""

    innings_map: dict[int, int] = {}

    for innings in package.innings:

        batting_team_id = team_map.get(
            innings.batting_team
        )

        if batting_team_id is None:
            raise ValueError(
                f"Unknown batting team: "
                f"{innings.batting_team}"
            )

        existing = session.scalar(
            select(MatchInnings).where(
                MatchInnings.match_id
                == package.match.match_id,
                MatchInnings.innings_number
                == innings.innings_number,
            )
        )

        if existing is not None:

            innings_map[
                innings.innings_number
            ] = existing.innings_id

            continue

        record = MatchInnings(
            match_id=package.match.match_id,
            innings_number=innings.innings_number,
            batting_team_id=batting_team_id,
        )

        session.add(record)
        session.flush()

        innings_map[
            innings.innings_number
        ] = record.innings_id

    return innings_map


def insert_deliveries(
    session: Session,
    package: TransformedMatchPackage,
    innings_map: dict[int, int],
    player_map: dict[str, int],
) -> dict[tuple[int, int], int]:
    """Insert deliveries and return delivery IDs."""

    delivery_map: dict[
        tuple[int, int],
        int,
    ] = {}

    for innings in package.innings:

        innings_id = innings_map[
            innings.innings_number
        ]

        for delivery in innings.deliveries:

            batter_id = player_map.get(
                delivery.batter
            )

            bowler_id = player_map.get(
                delivery.bowler
            )

            non_striker_id = player_map.get(
                delivery.non_striker
            )

            if batter_id is None:
                raise ValueError(
                    f"Unknown batter: "
                    f"{delivery.batter}"
                )

            if bowler_id is None:
                raise ValueError(
                    f"Unknown bowler: "
                    f"{delivery.bowler}"
                )

            if non_striker_id is None:
                raise ValueError(
                    f"Unknown non-striker: "
                    f"{delivery.non_striker}"
                )

            existing = session.scalar(
                select(Delivery).where(
                    Delivery.innings_id
                    == innings_id,
                    Delivery.over_number
                    == delivery.over_number,
                    Delivery.delivery_sequence
                    == delivery.delivery_sequence,
                )
            )

            if existing is not None:

                delivery_id = (
                    existing.delivery_id
                )

            else:

                record = Delivery(
                    innings_id=innings_id,
                    over_number=(
                        delivery.over_number
                    ),
                    delivery_sequence=(
                        delivery.delivery_sequence
                    ),
                    actual_delivery=(
                        delivery.actual_delivery
                    ),
                    batter_id=batter_id,
                    bowler_id=bowler_id,
                    non_striker_id=non_striker_id,
                    batter_runs=(
                        delivery.batter_runs
                    ),
                    total_runs=(
                        delivery.total_runs
                    ),
                )

                session.add(record)
                session.flush()

                delivery_id = (
                    record.delivery_id
                )

            delivery_map[
                (
                    innings.innings_number,
                    delivery.delivery_sequence,
                )
            ] = delivery_id

    return delivery_map


def insert_extras(
    session: Session,
    package: TransformedMatchPackage,
    delivery_map: dict[tuple[int, int], int],
) -> int:
    """Insert delivery extras."""

    count = 0

    for innings in package.innings:

        for delivery in innings.deliveries:

            if not delivery.extras:
                continue

            delivery_id = delivery_map[
                (
                    innings.innings_number,
                    delivery.delivery_sequence,
                )
            ]

            for extra in delivery.extras:

                existing = session.scalar(
                    select(DeliveryExtra).where(
                        DeliveryExtra.delivery_id
                        == delivery_id,
                        DeliveryExtra.extra_type
                        == extra.extra_type,
                        DeliveryExtra.runs
                        == extra.runs,
                    )
                )

                if existing is not None:
                    continue

                session.add(
                    DeliveryExtra(
                        delivery_id=delivery_id,
                        extra_type=extra.extra_type,
                        runs=extra.runs,
                    )
                )

                count += 1

    session.flush()

    return count


def insert_wickets(
    session: Session,
    package: TransformedMatchPackage,
    delivery_map: dict[tuple[int, int], int],
    player_map: dict[str, int],
) -> int:
    """Insert delivery wickets."""

    count = 0

    for innings in package.innings:

        for delivery in innings.deliveries:

            if not delivery.wickets:
                continue

            delivery_id = delivery_map[
                (
                    innings.innings_number,
                    delivery.delivery_sequence,
                )
            ]

            for wicket in delivery.wickets:

                player_out_id = player_map.get(
                    wicket.player_out
                )

                if player_out_id is None:
                    raise ValueError(
                        f"Unknown dismissed player: "
                        f"{wicket.player_out}"
                    )

                existing = session.scalar(
                    select(DeliveryWicket).where(
                        DeliveryWicket.delivery_id
                        == delivery_id,
                        DeliveryWicket.player_out_id
                        == player_out_id,
                        DeliveryWicket.kind
                        == wicket.kind,
                    )
                )

                if existing is not None:
                    continue

                session.add(
                    DeliveryWicket(
                        delivery_id=delivery_id,
                        player_out_id=player_out_id,
                        kind=wicket.kind,
                    )
                )

                count += 1

    session.flush()

    return count


def load_match(
    package: TransformedMatchPackage,
) -> None:
    """
    Load a complete match inside one transaction.
    """

    with Session(engine) as session:

        with session.begin():

            # ------------------------------------------
            # Reference entities
            # ------------------------------------------

            (
                team_map,
                player_map,
                venue_id,
            ) = build_reference_maps(
                session,
                package,
            )

            # ------------------------------------------
            # Match
            # ------------------------------------------

            insert_match(
                session,
                package,
                team_map,
                venue_id,
            )

            # ------------------------------------------
            # Match ↔ Team
            # ------------------------------------------

            insert_match_teams(
                session,
                package,
                team_map,
            )

            # ------------------------------------------
            # Innings
            # ------------------------------------------

            innings_map = insert_innings(
                session,
                package,
                team_map,
            )

            # ------------------------------------------
            # Deliveries
            # ------------------------------------------

            delivery_map = insert_deliveries(
                session,
                package,
                innings_map,
                player_map,
            )

            # ------------------------------------------
            # Extras
            # ------------------------------------------

            extras_count = insert_extras(
                session,
                package,
                delivery_map,
            )

            # ------------------------------------------
            # Wickets
            # ------------------------------------------

            wickets_count = insert_wickets(
                session,
                package,
                delivery_map,
                player_map,
            )

    print("Match loaded successfully.")
    print(
        f"Innings   : {len(innings_map)}"
    )
    print(
        f"Deliveries: {len(delivery_map)}"
    )
    print(
        f"Extras    : {extras_count}"
    )
    print(
        f"Wickets   : {wickets_count}"
    )
