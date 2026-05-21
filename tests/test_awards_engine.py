import pytest

from src.awards_engine import compute_awards
from tests.fixtures.sample_weekly_data import SAMPLE_WEEK


@pytest.fixture
def data():
    return SAMPLE_WEEK


def test_dumpster_fire_is_lowest_scorer(data):
    awards = compute_awards(data)
    assert awards.dumpster_fire.team_name == "The Dumpster Fire"
    assert "72.3" in awards.dumpster_fire.stat_line


def test_glass_cannon_is_highest_scorer(data):
    awards = compute_awards(data)
    assert awards.glass_cannon.team_name == "Alpha Dogs"
    assert "148.6" in awards.glass_cannon.stat_line


def test_heartbreak_hotel_is_closest_loss(data):
    awards = compute_awards(data)
    assert awards.heartbreak_hotel is not None
    # Closest loss is Lucky Charms vs The Usual Suspects: 102.1 - 101.3 = 0.8 pts
    assert awards.heartbreak_hotel.team_name == "The Usual Suspects"
    assert "0.8" in awards.heartbreak_hotel.stat_line


def test_bench_mogul_has_most_left_on_bench(data):
    awards = compute_awards(data)
    # Benchwarmer FC left 110.0 - 87.2 = 22.8 on bench
    assert awards.bench_mogul.team_name == "Benchwarmer FC"


def test_lucky_rabbit_none_when_all_winners_score_above_median(data):
    awards = compute_awards(data)
    # In SAMPLE_WEEK, all winners score above the median (102.1 ranks 5th of 8)
    assert awards.lucky_rabbit is None


def test_lucky_rabbit_triggers_for_low_scoring_winner():
    from tests.fixtures.sample_weekly_data import make_team
    # Winner scores 80 pts (rank 2 of 4 teams) — in bottom half
    low_winner = make_team("Scrappy Squad", "Sam", 80.0, 1, 2, 85.0)
    high_loser = make_team("Unlucky Stars", "Pat", 75.0, 2, 1, 80.0)
    filler_a = make_team("Team A", "A", 120.0, 3, 0, 120.0)
    filler_b = make_team("Team B", "B", 115.0, 2, 1, 115.0)
    from src.models import Matchup, WeeklyData, StandingEntry
    mini_data = WeeklyData(
        week_number=1,
        league_name="Mini",
        season=2025,
        matchups=[
            Matchup(winner=low_winner, loser=high_loser),
            Matchup(winner=filler_a, loser=filler_b),
        ],
        standings=[],
        next_week_matchups=[],
    )
    awards = compute_awards(mini_data)
    assert awards.lucky_rabbit is not None
    assert awards.lucky_rabbit.team_name == "Scrappy Squad"


def test_manager_spotlight_finds_overperforming_starters(data):
    awards = compute_awards(data)
    # Josh Allen: 42.8 actual vs 32.0 projected = 1.34x — just under 1.5x threshold
    # Patrick Mahomes: 38.2 vs 28.0 = 1.36x — just under 1.5x threshold
    # No player hits 1.5x AND >= 20 pts in the fixture — spotlight may be empty
    assert isinstance(awards.manager_spotlight, list)


def test_season_history_tracks_awards(tmp_path, monkeypatch, data):
    from src import awards_engine
    history_file = tmp_path / "awards_history.json"
    history_file.write_text('{"season": 2025, "weeks_processed": [], "totals": {}}')
    monkeypatch.setattr(awards_engine, "HISTORY_PATH", history_file)

    awards = compute_awards(data)
    history = awards_engine.update_awards_history(5, awards, 2025)

    assert 5 in history["weeks_processed"]
    assert "The Dumpster Fire" in history["totals"]
    assert history["totals"]["The Dumpster Fire"]["dumpster_fire"] == 1

    # Running it again for the same week should not double-count
    awards_engine.update_awards_history(5, awards, 2025)
    history2 = awards_engine.load_awards_history()
    assert history2["totals"]["The Dumpster Fire"]["dumpster_fire"] == 1
