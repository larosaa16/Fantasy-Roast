"""
Fetches weekly matchup data from Yahoo Fantasy via yfpy and normalizes
it into WeeklyData. Handles OAuth token refresh automatically.
"""

import os
from pathlib import Path

from yfpy.query import YahooFantasySportsQuery

from src.models import Matchup, PlayerResult, StandingEntry, TeamSnapshot, WeeklyData

TOKEN_DIR = Path(__file__).parent.parent / "data"


def fetch_weekly_data(week: int, season: int = 2025) -> WeeklyData:
    query = _make_query()
    league_id = os.environ["YAHOO_LEAGUE_ID"]
    game_code = os.environ.get("YAHOO_GAME_CODE", "nfl")
    league_name = os.environ.get("LEAGUE_NAME", "Fantasy League")

    scoreboard = query.get_league_scoreboard_by_week(chosen_week=week)
    standings_raw = query.get_league_standings()
    next_week_sb = query.get_league_scoreboard_by_week(chosen_week=week + 1)

    matchups = _parse_matchups(scoreboard)
    standings = _parse_standings(standings_raw)
    next_matchups = _parse_next_week_matchups(next_week_sb)

    return WeeklyData(
        week_number=week,
        league_name=league_name,
        season=season,
        matchups=matchups,
        standings=standings,
        next_week_matchups=next_matchups,
    )


def _make_query() -> YahooFantasySportsQuery:
    league_id = os.environ["YAHOO_LEAGUE_ID"]
    game_code = os.environ.get("YAHOO_GAME_CODE", "nfl")
    return YahooFantasySportsQuery(
        league_id=league_id,
        game_code=game_code,
        game_id=None,
        yahoo_consumer_key=os.environ["YAHOO_CLIENT_ID"],
        yahoo_consumer_secret=os.environ["YAHOO_CLIENT_SECRET"],
        yahoo_access_token_json=str(TOKEN_DIR / "token.json"),
        env_file_location=None,
        save_token_data_to_env_file=False,
    )


def _parse_matchups(scoreboard) -> list[Matchup]:
    matchups = []
    for raw in scoreboard.matchups.matchup:
        teams = raw.teams.team
        if len(teams) < 2:
            continue
        t1 = _parse_team(teams[0])
        t2 = _parse_team(teams[1])
        winner, loser = (t1, t2) if t1.score >= t2.score else (t2, t1)
        matchups.append(Matchup(winner=winner, loser=loser))
    return matchups


def _parse_team(raw_team) -> TeamSnapshot:
    roster = getattr(raw_team, "roster", None)
    starters, bench = [], []

    if roster:
        for player in getattr(roster, "players", []):
            p = getattr(player, "player", player)
            name = str(getattr(p, "full_name", "Unknown"))
            pos = str(getattr(p, "primary_position", "?"))
            actual = float(getattr(p, "player_points", {}).get("total", 0) or 0)
            projected = float(getattr(p, "projected_points", {}).get("total", 0) or 0)
            selected_pos = str(getattr(p, "selected_position", {}).get("position", "BN") or "BN")
            started = selected_pos != "BN"

            pr = PlayerResult(
                name=name,
                position=pos,
                actual_points=actual,
                projected_points=projected,
                started=started,
            )
            if started:
                starters.append(pr)
            else:
                bench.append(pr)

    started_score = sum(p.actual_points for p in starters)
    best_possible = _best_possible(starters, bench)

    record = getattr(raw_team, "team_standings", {})
    wins = int(getattr(record, "wins", 0) or 0)
    losses = int(getattr(record, "losses", 0) or 0)

    return TeamSnapshot(
        team_name=str(getattr(raw_team, "name", "Unknown Team")),
        manager_name=str(getattr(raw_team, "managers", [{}])[0].get("nickname", "Unknown")),
        score=float(getattr(raw_team, "team_points", {}).get("total", started_score) or started_score),
        wins=wins,
        losses=losses,
        starters=starters,
        bench=bench,
        best_possible_score=best_possible,
    )


def _best_possible(starters: list[PlayerResult], bench: list[PlayerResult]) -> float:
    """Best-ball score: for each position slot, take the highest scorer available."""
    all_players = starters + bench
    if not all_players:
        return 0.0
    # Simple approach: sum of top-N started players replaced by best bench equivalent
    # Full best-ball by position requires roster slot config; this approximates it
    started_total = sum(p.actual_points for p in starters)
    n_starters = len(starters)
    top_n = sorted(all_players, key=lambda p: p.actual_points, reverse=True)[:n_starters]
    return round(sum(p.actual_points for p in top_n), 2)


def _parse_standings(standings_raw) -> list[StandingEntry]:
    entries = []
    teams = getattr(standings_raw, "teams", [])
    for t in teams:
        team = getattr(t, "team", t)
        record = getattr(team, "team_standings", {})
        entries.append(
            StandingEntry(
                team_name=str(getattr(team, "name", "Unknown")),
                manager_name=str(getattr(team, "managers", [{}])[0].get("nickname", "Unknown")),
                wins=int(getattr(record, "wins", 0) or 0),
                losses=int(getattr(record, "losses", 0) or 0),
                points_for=float(getattr(record, "points_for", 0) or 0),
                points_against=float(getattr(record, "points_against", 0) or 0),
            )
        )
    return sorted(entries, key=lambda e: (e.wins, e.points_for), reverse=True)


def _parse_next_week_matchups(scoreboard) -> list[tuple[str, str]]:
    pairs = []
    for raw in scoreboard.matchups.matchup:
        teams = raw.teams.team
        if len(teams) < 2:
            continue
        t1 = str(getattr(teams[0], "name", "Team A"))
        t2 = str(getattr(teams[1], "name", "Team B"))
        pairs.append((t1, t2))
    return pairs
