"""Shared fixture for tests — a realistic 4-matchup week."""

from src.models import Matchup, PlayerResult, StandingEntry, TeamSnapshot, WeeklyData


def make_player(name: str, pos: str, actual: float, projected: float, started: bool) -> PlayerResult:
    return PlayerResult(name=name, position=pos, actual_points=actual, projected_points=projected, started=started)


def make_team(
    name: str,
    manager: str,
    score: float,
    wins: int,
    losses: int,
    best_possible: float,
    starters: list[PlayerResult] | None = None,
    bench: list[PlayerResult] | None = None,
) -> TeamSnapshot:
    return TeamSnapshot(
        team_name=name,
        manager_name=manager,
        score=score,
        wins=wins,
        losses=losses,
        starters=starters or [],
        bench=bench or [],
        best_possible_score=best_possible,
    )


SAMPLE_WEEK = WeeklyData(
    week_number=5,
    league_name="Test League",
    season=2025,
    matchups=[
        Matchup(
            winner=make_team("Alpha Dogs", "Alice", 148.6, 4, 0, 148.6, starters=[
                make_player("Patrick Mahomes", "QB", 38.2, 28.0, True),
                make_player("Davante Adams", "WR", 22.4, 18.0, True),
            ], bench=[
                make_player("Gus Edwards", "RB", 4.1, 8.0, False),
            ]),
            loser=make_team("Benchwarmer FC", "Bob", 87.2, 1, 3, 110.0, starters=[
                make_player("Jared Goff", "QB", 12.4, 22.0, True),
                make_player("Elijah Mitchell", "RB", 6.8, 14.0, True),
            ], bench=[
                make_player("Jaylen Waddle", "WR", 28.4, 15.0, False),
            ]),
        ),
        Matchup(
            winner=make_team("Lucky Charms", "Carol", 102.1, 2, 2, 115.0, starters=[
                make_player("Geno Smith", "QB", 18.0, 21.0, True),
            ], bench=[]),
            loser=make_team("The Usual Suspects", "Dave", 101.3, 3, 1, 118.0, starters=[
                make_player("Justin Herbert", "QB", 24.6, 28.0, True),
            ], bench=[]),
        ),
        Matchup(
            winner=make_team("Touchdown Bandits", "Eve", 132.4, 3, 1, 138.0, starters=[
                make_player("Josh Allen", "QB", 42.8, 32.0, True),
            ], bench=[]),
            loser=make_team("Gridiron Ghosts", "Frank", 98.6, 1, 3, 99.0, starters=[
                make_player("Kirk Cousins", "QB", 14.2, 22.0, True),
            ], bench=[]),
        ),
        Matchup(
            winner=make_team("Fantasy Kings", "Grace", 118.9, 2, 2, 120.0, starters=[
                make_player("Lamar Jackson", "QB", 35.1, 30.0, True),
            ], bench=[]),
            loser=make_team("The Dumpster Fire", "Hank", 72.3, 0, 4, 95.0, starters=[
                make_player("Mac Jones", "QB", 8.6, 20.0, True),
            ], bench=[
                make_player("DK Metcalf", "WR", 24.0, 18.0, False),
            ]),
        ),
    ],
    standings=[
        StandingEntry("Alpha Dogs", "Alice", 4, 0, 620.0, 480.0),
        StandingEntry("Touchdown Bandits", "Eve", 3, 1, 540.0, 490.0),
        StandingEntry("The Usual Suspects", "Dave", 3, 1, 510.0, 460.0),
        StandingEntry("Fantasy Kings", "Grace", 2, 2, 480.0, 495.0),
        StandingEntry("Lucky Charms", "Carol", 2, 2, 470.0, 500.0),
        StandingEntry("Benchwarmer FC", "Bob", 1, 3, 440.0, 540.0),
        StandingEntry("Gridiron Ghosts", "Frank", 1, 3, 430.0, 530.0),
        StandingEntry("The Dumpster Fire", "Hank", 0, 4, 390.0, 600.0),
    ],
    next_week_matchups=[
        ("Alpha Dogs", "Touchdown Bandits"),
        ("The Usual Suspects", "Fantasy Kings"),
        ("Lucky Charms", "Gridiron Ghosts"),
        ("Benchwarmer FC", "The Dumpster Fire"),
    ],
)
