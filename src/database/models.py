from datetime import date

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Team(Base):
    __tablename__ = "dim_team"

    team_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    team_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )


class TeamAlias(Base):
    __tablename__ = "dim_team_alias"

    team_alias_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("dim_team.team_id"),
        nullable=False,
    )

    raw_team_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )


class Player(Base):
    __tablename__ = "dim_player"

    player_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    player_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    registry_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )


class Venue(Base):
    __tablename__ = "dim_venue"

    venue_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    venue_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    city: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "venue_name",
            "city",
            name="uq_venue_name_city",
        ),
    )


class Match(Base):
    __tablename__ = "dim_match"

    match_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    season: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    match_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    venue_id: Mapped[int | None] = mapped_column(
        ForeignKey("dim_venue.venue_id"),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    toss_winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("dim_team.team_id"),
        nullable=True,
    )

    toss_decision: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("dim_team.team_id"),
        nullable=True,
    )

    match_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    player_of_match: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )


class MatchTeam(Base):
    __tablename__ = "match_team"

    match_id: Mapped[int] = mapped_column(
        ForeignKey("dim_match.match_id"),
        primary_key=True,
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("dim_team.team_id"),
        primary_key=True,
    )


class MatchInnings(Base):
    __tablename__ = "match_innings"

    innings_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    match_id: Mapped[int] = mapped_column(
        ForeignKey("dim_match.match_id"),
        nullable=False,
    )

    innings_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    batting_team_id: Mapped[int] = mapped_column(
        ForeignKey("dim_team.team_id"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "match_id",
            "innings_number",
            name="uq_match_innings_number",
        ),
    )


class Delivery(Base):
    __tablename__ = "fact_delivery"

    delivery_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    innings_id: Mapped[int] = mapped_column(
        ForeignKey("match_innings.innings_id"),
        nullable=False,
    )

    over_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    delivery_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    actual_delivery: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    batter_id: Mapped[int] = mapped_column(
        ForeignKey("dim_player.player_id"),
        nullable=False,
    )

    bowler_id: Mapped[int] = mapped_column(
        ForeignKey("dim_player.player_id"),
        nullable=False,
    )

    non_striker_id: Mapped[int] = mapped_column(
        ForeignKey("dim_player.player_id"),
        nullable=False,
    )

    batter_runs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_runs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    __table_args__ = (
        UniqueConstraint(
            "innings_id",
            "over_number",
            "delivery_sequence",
            name="uq_delivery_position",
        ),
    )

class DeliveryExtra(Base):
    __tablename__ = "delivery_extras"

    delivery_extra_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    delivery_id: Mapped[int] = mapped_column(
        ForeignKey("fact_delivery.delivery_id"),
        nullable=False,
    )

    extra_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    runs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


class DeliveryWicket(Base):
    __tablename__ = "delivery_wickets"

    delivery_wicket_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    delivery_id: Mapped[int] = mapped_column(
        ForeignKey("fact_delivery.delivery_id"),
        nullable=False,
    )

    player_out_id: Mapped[int] = mapped_column(
        ForeignKey("dim_player.player_id"),
        nullable=False,
    )

    kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    
class ETLFileQualityIssue(Base):
    __tablename__ = "etl_file_quality_issue"

    quality_issue_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    file_log_id: Mapped[int] = mapped_column(
        ForeignKey("etl_file_log.file_log_id"),
        nullable=False,
    )

    rule_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    field: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )