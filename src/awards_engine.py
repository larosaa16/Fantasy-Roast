"""
Computes weekly fantasy awards from WeeklyData — no AI involved.
Also maintains the season-long awards history in data/awards_history.json.
"""

import json
from pathlib import Path

from src.models import AwardResult, AwardResults, Matchup, TeamSnapshot, WeeklyData

HISTORY_PATH = Path(__file__).parent.parent / "data" / "awards_history.json"

AWARD_KEYS = [
    "dumpster_fire",
    "lucky_rabbit",
    "bench_mogul",
    "glass_cannon",
    "heartbreak_hotel",
    "manager_spotlight",
]


def compute_awards(data: WeeklyData) -> AwardResults:
    all_teams: list[TeamSnapshot] = []
    for m in data.matchups:
        all_teams.append(m.winner)
        all_teams.append(m.loser)

    scores = sorted(all_teams, key=lambda t: t.score)
    score_rank = {t.team_name: i + 1 for i, t in enumerate(scores)}

    dumpster = scores[0]
    dumpster_award = AwardResult(
        award_name="Dumpster Fire Award",
        team_name=dumpster.team_name,
        manager_name=dumpster.manager_name,
        stat_line=f"{dumpster.score} pts — lowest score of the week",
    )

    # Lucky Rabbit: a winner whose score ranked bottom-half of all teams
    lucky_rabbit_award = None
    n_teams = len(all_teams)
    for m in data.matchups:
        rank = score_rank[m.winner.team_name]
        if rank <= n_teams // 2:
            lucky_rabbit_award = AwardResult(
                award_name="Lucky Rabbit Award",
                team_name=m.winner.team_name,
                manager_name=m.winner.manager_name,
                stat_line=(
                    f"Won with {m.winner.score} pts — ranked {rank}{_ordinal(rank)} "
                    f"out of {n_teams} teams this week"
                ),
                extra={"opponent_score": m.loser.score},
            )
            break

    # Bench Mogul: most points left on the bench
    bench_candidates = [
        (t, t.best_possible_score - t.score)
        for t in all_teams
        if t.best_possible_score > t.score
    ]
    if bench_candidates:
        bench_team, left_on_bench = max(bench_candidates, key=lambda x: x[1])
        bench_award = AwardResult(
            award_name="Bench Mogul Award",
            team_name=bench_team.team_name,
            manager_name=bench_team.manager_name,
            stat_line=(
                f"Left {round(left_on_bench, 2)} pts on the bench "
                f"(started {bench_team.score}, best possible was {bench_team.best_possible_score})"
            ),
            extra={"left_on_bench": round(left_on_bench, 2)},
        )
    else:
        top = scores[-1]
        bench_award = AwardResult(
            award_name="Bench Mogul Award",
            team_name=top.team_name,
            manager_name=top.manager_name,
            stat_line="No bench data available",
        )

    glass_cannon = scores[-1]
    glass_award = AwardResult(
        award_name="Glass Cannon Award",
        team_name=glass_cannon.team_name,
        manager_name=glass_cannon.manager_name,
        stat_line=f"{glass_cannon.score} pts — highest score of the week",
    )

    # Heartbreak Hotel: closest loss
    heartbreak_award = None
    if data.matchups:
        closest = min(data.matchups, key=lambda m: m.margin)
        heartbreak_award = AwardResult(
            award_name="Heartbreak Hotel Award",
            team_name=closest.loser.team_name,
            manager_name=closest.loser.manager_name,
            stat_line=f"Lost by {closest.margin} pts to {closest.winner.team_name}",
            extra={"margin": closest.margin, "winner": closest.winner.team_name},
        )

    # Manager Spotlight: starters who massively outperformed projection (1.5x+)
    spotlight_awards: list[AwardResult] = []
    for t in all_teams:
        for p in t.starters:
            if p.projected_points > 0 and p.actual_points >= p.projected_points * 1.5 and p.actual_points >= 20:
                spotlight_awards.append(
                    AwardResult(
                        award_name="Manager Spotlight",
                        team_name=t.team_name,
                        manager_name=t.manager_name,
                        stat_line=(
                            f"{p.name} ({p.position}) delivered {p.actual_points} pts "
                            f"(projected: {p.projected_points})"
                        ),
                        extra={"player": p.name, "position": p.position},
                    )
                )
    spotlight_awards = spotlight_awards[:2]

    return AwardResults(
        dumpster_fire=dumpster_award,
        lucky_rabbit=lucky_rabbit_award,
        bench_mogul=bench_award,
        glass_cannon=glass_award,
        heartbreak_hotel=heartbreak_award,
        manager_spotlight=spotlight_awards,
    )


def update_awards_history(week: int, awards: AwardResults, season: int) -> dict:
    history = _load_history()

    if week in history.get("weeks_processed", []):
        return history

    history.setdefault("weeks_processed", []).append(week)
    history.setdefault("season", season)
    totals: dict[str, dict[str, int]] = history.setdefault("totals", {})

    def _record(award: AwardResult | None, key: str) -> None:
        if award is None:
            return
        team = award.team_name
        totals.setdefault(team, {})
        totals[team][key] = totals[team].get(key, 0) + 1
        totals[team]["total"] = totals[team].get("total", 0) + 1

    _record(awards.dumpster_fire, "dumpster_fire")
    _record(awards.lucky_rabbit, "lucky_rabbit")
    _record(awards.bench_mogul, "bench_mogul")
    _record(awards.glass_cannon, "glass_cannon")
    _record(awards.heartbreak_hotel, "heartbreak_hotel")
    for s in awards.manager_spotlight:
        _record(s, "manager_spotlight")

    HISTORY_PATH.write_text(json.dumps(history, indent=2))
    return history


def load_awards_history() -> dict:
    return _load_history()


def _load_history() -> dict:
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text())
    return {"season": 2025, "weeks_processed": [], "totals": {}}


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
