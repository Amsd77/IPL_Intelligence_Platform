from src.ingestion.parser import MatchRecord
from src.validation.models import DataQualityResult


VALID_TOSS_DECISIONS = {
    "bat",
    "field",
}


def _check_winner(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ001: Winner must be one of the match teams."""

    if not match.winner:
        return

    team_names = {
        team.name.strip()
        for team in match.teams
    }

    if match.winner.strip() not in team_names:
        result.add_error(
            rule_id="DQ001",
            field="winner",
            message=(
                f"Winner '{match.winner}' is not one "
                "of the match teams."
            ),
        )


def _check_toss_winner(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ002: Toss winner must be one of the match teams."""

    if not match.toss_winner:
        return

    team_names = {
        team.name.strip()
        for team in match.teams
    }

    if match.toss_winner.strip() not in team_names:
        result.add_error(
            rule_id="DQ002",
            field="toss_winner",
            message=(
                f"Toss winner '{match.toss_winner}' "
                "is not one of the match teams."
            ),
        )


def _check_toss_decision(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ003: Toss decision must be bat or field."""

    if not match.toss_decision:
        return

    decision = match.toss_decision.strip().lower()

    if decision not in VALID_TOSS_DECISIONS:
        result.add_error(
            rule_id="DQ003",
            field="toss_decision",
            message=(
                f"Invalid toss decision: "
                f"'{match.toss_decision}'."
            ),
        )


def _check_innings_numbers(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """
    DQ004/DQ005:
    Innings numbers must be unique and sequential.
    """

    innings_numbers = [
        innings.innings_number
        for innings in match.innings
    ]

    if len(innings_numbers) != len(
        set(innings_numbers)
    ):
        result.add_error(
            rule_id="DQ004",
            field="innings",
            message="Duplicate innings numbers found.",
        )

    expected = list(
        range(1, len(innings_numbers) + 1)
    )

    if sorted(innings_numbers) != expected:
        result.add_error(
            rule_id="DQ005",
            field="innings",
            message=(
                "Innings numbers are not sequential. "
                f"Found: {innings_numbers}."
            ),
        )


def _check_batting_teams(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ006: Every innings must have a valid batting team."""

    team_names = {
        team.name.strip()
        for team in match.teams
    }

    for innings in match.innings:

        batting_team = (
            innings.batting_team.strip()
            if innings.batting_team
            else ""
        )

        if not batting_team:
            continue

        if batting_team not in team_names:
            result.add_error(
                rule_id="DQ006",
                field=(
                    f"innings[{innings.innings_number}]"
                    ".batting_team"
                ),
                message=(
                    f"Batting team '{batting_team}' "
                    "is not one of the match teams."
                ),
            )


# def _check_delivery_positions(
#     match: MatchRecord,
#     result: DataQualityResult,
# ) -> None:
#     """DQ007: Delivery positions must be unique."""

#     for innings in match.innings:

#         positions: set[tuple[int, int]] = set()

#         for delivery in innings.deliveries:

#             position = (
#                 delivery.over_number,
#                 delivery.ball_number,
#             )

#             if position in positions:

#                 result.add_error(
#                     rule_id="DQ007",
#                     field=(
#                         f"innings[{innings.innings_number}]"
#                         ".deliveries"
#                     ),
#                     message=(
#                         "Duplicate delivery position "
#                         f"found: over={delivery.over_number}, "
#                         f"ball={delivery.ball_number}."
#                     ),
#                 )

#             positions.add(position)


def _check_run_consistency(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ008: Total runs cannot be less than batter runs."""

    for innings in match.innings:

        for index, delivery in enumerate(
            innings.deliveries,
            start=1,
        ):

            if (
                delivery.total_runs
                < delivery.batter_runs
            ):
                result.add_error(
                    rule_id="DQ008",
                    field=(
                        f"innings[{innings.innings_number}]"
                        f".deliveries[{index}]"
                    ),
                    message=(
                        "Total runs cannot be less than "
                        "batter runs."
                    ),
                )


def _check_player_of_match(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ009: Player of match should exist in player list."""

    if not match.player_of_match:
        return

    player_names = {
        player.name.strip()
        for player in match.players
    }

    for player_of_match in match.player_of_match:

        player_name = player_of_match.strip()

        if not player_name:
            continue

        if player_name not in player_names:

            result.add_warning(
                rule_id="DQ009",
                field="player_of_match",
                message=(
                    f"Player of match "
                    f"'{player_name}' "
                    "was not found in the match player list."
                ),
            )

def _check_city(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ010: Venue city completeness is a warning."""

    if not match.venue:
        result.add_warning(
            rule_id="DQ010",
            field="venue",
            message="Venue information is missing.",
        )
        return

    if not match.venue.city or not match.venue.city.strip():
        result.add_warning(
            rule_id="DQ010",
            field="venue.city",
            message="Venue city is missing.",
        )


def _check_player_of_match_missing(
    match: MatchRecord,
    result: DataQualityResult,
) -> None:
    """DQ011: Missing player of match is a warning."""

    if not match.player_of_match:

        result.add_warning(
            rule_id="DQ011",
            field="player_of_match",
            message="Player of match is missing.",
        )

def run_data_quality_checks(
    match: MatchRecord,
) -> DataQualityResult:
    """
    Run all data-quality checks for a parsed match.

    Returns:
        DataQualityResult containing errors and warnings.
    """

    result = DataQualityResult()

    _check_winner(
        match,
        result,
    )

    _check_toss_winner(
        match,
        result,
    )

    _check_toss_decision(
        match,
        result,
    )

    _check_innings_numbers(
        match,
        result,
    )

    _check_batting_teams(
        match,
        result,
    )

    # _check_delivery_positions(
    #     match,
    #     result,
    # )

    _check_run_consistency(
        match,
        result,
    )

    _check_player_of_match(
        match,
        result,
    )

    _check_city(
        match,
        result,
    )

    _check_player_of_match_missing(
        match,
        result,
    )

    return result