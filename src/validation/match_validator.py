from dataclasses import dataclass, field

from src.ingestion.parser import (
    DeliveryRecord,
    InningsRecord,
    MatchRecord,
    PlayerRecord,
)


@dataclass(frozen=True)
class ValidationError:
    """Represents one validation failure."""

    field: str
    message: str


@dataclass
class ValidationResult:
    """Result of validating a parsed match."""

    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True when no validation errors exist."""

        return len(self.errors) == 0

    def add_error(
        self,
        field: str,
        message: str,
    ) -> None:
        """Add a validation error."""

        self.errors.append(
            ValidationError(
                field=field,
                message=message,
            )
        )
        
def _validate_match(
    match: MatchRecord,
    result: ValidationResult,
) -> None:
    """Validate match-level fields."""

    if match.match_id <= 0:
        result.add_error(
            "match_id",
            "Match ID must be greater than zero.",
        )

    if not match.season:
        result.add_error(
            "season",
            "Season is required.",
        )

    if not match.match_date:
        result.add_error(
            "match_date",
            "Match date is required.",
        )

    if len(match.teams) != 2:
        result.add_error(
            "teams",
            f"Expected exactly 2 teams, found {len(match.teams)}.",
        )

    team_names = [
        team.name.strip()
        for team in match.teams
        if team.name
    ]

    if len(team_names) != len(set(team_names)):
        result.add_error(
            "teams",
            "Match contains duplicate teams.",
        )
        
def _validate_players(
    match: MatchRecord,
    result: ValidationResult,
) -> None:
    """Validate match players."""

    if not match.players:
        result.add_error(
            "players",
            "No players were found.",
        )
        return

    seen_names: set[str] = set()

    for player in match.players:

        name = player.name.strip()

        if not name:
            result.add_error(
                "players",
                "Player name cannot be empty.",
            )
            continue

        if name in seen_names:
            result.add_error(
                f"players.{name}",
                "Duplicate player record.",
            )

        seen_names.add(name)

        if player.registry_id is not None:
            if not player.registry_id.strip():
                result.add_error(
                    f"players.{name}.registry_id",
                    "Registry ID cannot be empty.",
                )
                
def _validate_innings(
    match: MatchRecord,
    result: ValidationResult,
) -> None:
    """Validate innings-level data."""

    if not match.innings:
        result.add_error(
            "innings",
            "Match contains no innings.",
        )
        return

    match_teams = {
        team.name
        for team in match.teams
    }

    for innings in match.innings:

        field_name = (
            f"innings[{innings.innings_number}]"
        )

        if not innings.batting_team:
            result.add_error(
                f"{field_name}.batting_team",
                "Batting team is required.",
            )

        elif innings.batting_team not in match_teams:
            result.add_error(
                f"{field_name}.batting_team",
                (
                    f"Batting team '{innings.batting_team}' "
                    "is not one of the match teams."
                ),
            )

        if not innings.deliveries:
            result.add_error(
                f"{field_name}.deliveries",
                "Innings contains no deliveries.",
            )
            
def _validate_delivery(
    delivery: DeliveryRecord,
    innings_number: int,
    delivery_index: int,
    known_players: set[str],
    result: ValidationResult,
) -> None:
    """Validate one delivery."""

    prefix = (
        f"innings[{innings_number}]"
        f".deliveries[{delivery_index}]"
    )

    if not delivery.batter:
        result.add_error(
            f"{prefix}.batter",
            "Batter is required.",
        )

    elif delivery.batter not in known_players:
        result.add_error(
            f"{prefix}.batter",
            f"Unknown batter: {delivery.batter}.",
        )

    if not delivery.bowler:
        result.add_error(
            f"{prefix}.bowler",
            "Bowler is required.",
        )

    elif delivery.bowler not in known_players:
        result.add_error(
            f"{prefix}.bowler",
            f"Unknown bowler: {delivery.bowler}.",
        )

    if not delivery.non_striker:
        result.add_error(
            f"{prefix}.non_striker",
            "Non-striker is required.",
        )

    elif delivery.non_striker not in known_players:
        result.add_error(
            f"{prefix}.non_striker",
            (
                f"Unknown non-striker: "
                f"{delivery.non_striker}."
            ),
        )

    if delivery.over_number < 0:
        result.add_error(
            f"{prefix}.over_number",
            "Over number cannot be negative.",
        )

    if delivery.ball_number <= 0:
        result.add_error(
            f"{prefix}.ball_number",
            "Ball number must be greater than zero.",
        )

    if delivery.batter_runs < 0:
        result.add_error(
            f"{prefix}.batter_runs",
            "Batter runs cannot be negative.",
        )

    if delivery.total_runs < 0:
        result.add_error(
            f"{prefix}.total_runs",
            "Total runs cannot be negative.",
        )
        
    for extra in delivery.extras:

        if not extra.extra_type.strip():
            result.add_error(
                f"{prefix}.extras",
                "Extra type cannot be empty.",
            )

        if extra.runs < 0:
            result.add_error(
                f"{prefix}.extras.{extra.extra_type}",
                "Extra runs cannot be negative.",
            )
            
    for wicket in delivery.wickets:

        if not wicket.player_out:
            result.add_error(
                f"{prefix}.wickets",
                "Wicket must contain player_out.",
            )

        elif wicket.player_out not in known_players:
            result.add_error(
                f"{prefix}.wickets.player_out",
                (
                    f"Unknown player dismissed: "
                    f"{wicket.player_out}."
                ),
            )

        if not wicket.kind:
            result.add_error(
                f"{prefix}.wickets.kind",
                "Wicket kind cannot be empty.",
            )
            
    for wicket in delivery.wickets:

        if not wicket.player_out:
            result.add_error(
                f"{prefix}.wickets",
                "Wicket must contain player_out.",
            )

        elif wicket.player_out not in known_players:
            result.add_error(
                f"{prefix}.wickets.player_out",
                (
                    f"Unknown player dismissed: "
                    f"{wicket.player_out}."
                ),
            )

        if not wicket.kind:
            result.add_error(
                f"{prefix}.wickets.kind",
                "Wicket kind cannot be empty.",
            )
            
def _validate_all_deliveries(
    match: MatchRecord,
    result: ValidationResult,
) -> None:
    """Validate all deliveries in the match."""

    known_players = {
        player.name
        for player in match.players
    }

    for innings in match.innings:

        for delivery_index, delivery in enumerate(
            innings.deliveries,
            start=1,
        ):
            _validate_delivery(
                delivery=delivery,
                innings_number=innings.innings_number,
                delivery_index=delivery_index,
                known_players=known_players,
                result=result,
            )
            
def validate_match(
    match: MatchRecord,
) -> ValidationResult:
    """
    Validate a parsed match.

    Returns a ValidationResult containing all
    discovered validation errors.
    """

    result = ValidationResult()

    _validate_match(
        match=match,
        result=result,
    )

    _validate_players(
        match=match,
        result=result,
    )

    _validate_innings(
        match=match,
        result=result,
    )

    _validate_all_deliveries(
        match=match,
        result=result,
    )

    return result