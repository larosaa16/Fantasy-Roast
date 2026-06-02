from dataclasses import dataclass, field


@dataclass
class PlayerResult:
    name: str
    position: str
    actual_points: float
    projected_points: float
    started: bool


@dataclass
class TeamSnapshot:
    team_name: str
    manager_name: str
    score: float
    wins: int
    losses: int
    starters: list[PlayerResult] = field(default_factory=list)
    bench: list[PlayerResult] = field(default_factory=list)
    best_possible_score: float = 0.0


@dataclass
class Matchup:
    winner: TeamSnapshot
    loser: TeamSnapshot

    @property
    def margin(self) -> float:
        return round(self.winner.score - self.loser.score, 2)


@dataclass
class StandingEntry:
    team_name: str
    manager_name: str
    wins: int
    losses: int
    points_for: float
    points_against: float


@dataclass
class AwardResult:
    award_name: str
    team_name: str
    manager_name: str
    stat_line: str
    extra: dict = field(default_factory=dict)


@dataclass
class AwardResults:
    dumpster_fire: AwardResult
    lucky_rabbit: AwardResult | None
    bench_mogul: AwardResult
    glass_cannon: AwardResult
    heartbreak_hotel: AwardResult | None
    manager_spotlight: list[AwardResult] = field(default_factory=list)


@dataclass
class WeeklyData:
    week_number: int
    league_name: str
    season: int
    matchups: list[Matchup]
    standings: list[StandingEntry]
    next_week_matchups: list[tuple[str, str]]
    awards: AwardResults | None = None
