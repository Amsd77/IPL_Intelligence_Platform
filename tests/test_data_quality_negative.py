from datetime import date

from src.ingestion.parser import (
    DeliveryRecord,
    InningsRecord,
    MatchRecord,
    PlayerRecord,
    TeamRecord,
    VenueRecord,
)

from src.validation.data_quality import (
    run_data_quality_checks,
)


def create_delivery(
    *,
    over_number: int = 0,
    ball_number: int = 1,
    batter_runs: int = 0,
    total_runs: int = 0,
) -> DeliveryRecord:

    return DeliveryRecord(
        over_number=over_number,
        ball_number=ball_number,
        actual_delivery="0.1",
        batter="Player A",
        bowler="Player B",
        non_striker="Player C",
        batter_runs=batter_runs,
        total_runs=total_runs,
        extras=(),
        wickets=(),
    )


def create_base_match() -> MatchRecord:

    teams = (
        TeamRecord(
            name="Sunrisers Hyderabad",
        ),
        TeamRecord(
            name="Royal Challengers Bangalore",
        ),
    )

    players = (
        PlayerRecord(
            name="Player A",
            registry_id=None,
        ),
        PlayerRecord(
            name="Player B",
            registry_id=None,
        ),
        PlayerRecord(
            name="Player C",
            registry_id=None,
        ),
    )

    delivery = create_delivery()

    innings = (
        InningsRecord(
            innings_number=1,
            batting_team="Sunrisers Hyderabad",
            deliveries=(delivery,),
        ),
    )

    return MatchRecord(
        match_id=999999,
        season="2026",
        match_date=date(2026, 1, 1),
        teams=teams,
        venue=VenueRecord(
            name="Test Stadium",
            city="Test City",
        ),
        toss_winner="Sunrisers Hyderabad",
        toss_decision="bat",
        winner="Sunrisers Hyderabad",
        match_type="T20",
        gender="male",
        player_of_match=(),
        players=players,
        innings=innings,
    )


def test_invalid_winner_is_error():

    match = create_base_match()

    match = match.__class__(
        **{
            **match.__dict__,
            "winner": "Chennai Super Kings",
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ001"
        for issue in result.errors
    )


def test_invalid_toss_winner_is_error():

    match = create_base_match()

    match = match.__class__(
        **{
            **match.__dict__,
            "toss_winner": "Chennai Super Kings",
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ002"
        for issue in result.errors
    )


def test_invalid_toss_decision_is_error():

    match = create_base_match()

    match = match.__class__(
        **{
            **match.__dict__,
            "toss_decision": "something_invalid",
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ003"
        for issue in result.errors
    )


def test_duplicate_innings_is_error():

    match = create_base_match()

    delivery = create_delivery()

    duplicate_innings = (
        InningsRecord(
            innings_number=1,
            batting_team="Sunrisers Hyderabad",
            deliveries=(delivery,),
        ),
        InningsRecord(
            innings_number=1,
            batting_team="Royal Challengers Bangalore",
            deliveries=(delivery,),
        ),
    )

    match = match.__class__(
        **{
            **match.__dict__,
            "innings": duplicate_innings,
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ004"
        for issue in result.errors
    )


def test_non_sequential_innings_is_error():

    match = create_base_match()

    delivery = create_delivery()

    invalid_innings = (
        InningsRecord(
            innings_number=1,
            batting_team="Sunrisers Hyderabad",
            deliveries=(delivery,),
        ),
        InningsRecord(
            innings_number=3,
            batting_team="Royal Challengers Bangalore",
            deliveries=(delivery,),
        ),
    )

    match = match.__class__(
        **{
            **match.__dict__,
            "innings": invalid_innings,
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ005"
        for issue in result.errors
    )


def test_invalid_batting_team_is_error():

    match = create_base_match()

    delivery = create_delivery()

    invalid_innings = (
        InningsRecord(
            innings_number=1,
            batting_team="Chennai Super Kings",
            deliveries=(delivery,),
        ),
    )

    match = match.__class__(
        **{
            **match.__dict__,
            "innings": invalid_innings,
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ006"
        for issue in result.errors
    )


def test_total_runs_less_than_batter_runs_is_error():

    match = create_base_match()

    invalid_delivery = create_delivery(
        batter_runs=4,
        total_runs=2,
    )

    innings = (
        InningsRecord(
            innings_number=1,
            batting_team="Sunrisers Hyderabad",
            deliveries=(invalid_delivery,),
        ),
    )

    match = match.__class__(
        **{
            **match.__dict__,
            "innings": innings,
        }
    )

    result = run_data_quality_checks(match)

    assert not result.is_valid

    assert any(
        issue.rule_id == "DQ008"
        for issue in result.errors
    )


def test_unknown_player_of_match_is_warning():

    match = create_base_match()

    match = match.__class__(
        **{
            **match.__dict__,
            "player_of_match": (
                "Unknown Player",
            ),
        }
    )

    result = run_data_quality_checks(match)

    assert result.is_valid

    assert any(
        issue.rule_id == "DQ009"
        for issue in result.warnings
    )


def test_missing_city_is_warning():

    match = create_base_match()

    match = match.__class__(
        **{
            **match.__dict__,
            "venue": VenueRecord(
                name="Test Stadium",
                city=None,
            ),
        }
    )

    result = run_data_quality_checks(match)

    assert result.is_valid

    assert any(
        issue.rule_id == "DQ010"
        for issue in result.warnings
    )


def test_missing_player_of_match_is_warning():

    match = create_base_match()

    match = match.__class__(
        **{
            **match.__dict__,
            "player_of_match": (),
        }
    )

    result = run_data_quality_checks(match)

    assert result.is_valid

    assert any(
        issue.rule_id == "DQ011"
        for issue in result.warnings
    )
    
    