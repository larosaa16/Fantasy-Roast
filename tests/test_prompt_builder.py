import pytest

from src.awards_engine import compute_awards
from src.prompt_builder import build_assembly_prompt, build_awards_prompt, build_matchup_prompts
from tests.fixtures.sample_weekly_data import SAMPLE_WEEK


@pytest.fixture
def data_with_awards():
    d = SAMPLE_WEEK
    d.awards = compute_awards(d)
    return d


def test_matchup_prompts_count_matches_matchups(data_with_awards):
    prompts = build_matchup_prompts(data_with_awards)
    assert len(prompts) == len(data_with_awards.matchups)


def test_matchup_prompt_contains_scores(data_with_awards):
    prompts = build_matchup_prompts(data_with_awards)
    first = prompts[0]["messages"][0]["content"]
    assert "148.6" in first
    assert "87.2" in first
    assert "Alpha Dogs" in first
    assert "Benchwarmer FC" in first


def test_matchup_prompt_contains_player_names(data_with_awards):
    prompts = build_matchup_prompts(data_with_awards)
    first = prompts[0]["messages"][0]["content"]
    assert "Patrick Mahomes" in first
    assert "Jared Goff" in first


def test_awards_prompt_contains_award_data(data_with_awards):
    history = {"totals": {}, "weeks_processed": []}
    prompt = build_awards_prompt(data_with_awards, history)
    content = prompt["messages"][0]["content"]
    assert "Dumpster Fire" in content
    assert "Glass Cannon" in content
    assert "Heartbreak Hotel" in content


def test_awards_prompt_includes_season_leaderboard(data_with_awards):
    history = {
        "totals": {"Alpha Dogs": {"glass_cannon": 2, "total": 2}},
        "weeks_processed": [1, 2],
    }
    prompt = build_awards_prompt(data_with_awards, history)
    content = prompt["messages"][0]["content"]
    assert "SEASON AWARD LEADERBOARD" in content
    assert "Alpha Dogs" in content


def test_assembly_prompt_contains_standings(data_with_awards):
    prompt = build_assembly_prompt(data_with_awards, ["<mock>"], "<mock awards>")
    content = prompt["messages"][0]["content"]
    assert "Alpha Dogs" in content
    assert "Touchdown Bandits" in content


def test_assembly_prompt_contains_next_week_matchups(data_with_awards):
    prompt = build_assembly_prompt(data_with_awards, ["<mock>"], "<mock awards>")
    content = prompt["messages"][0]["content"]
    assert "Alpha Dogs vs Touchdown Bandits" in content


def test_system_prompt_is_set(data_with_awards):
    prompts = build_matchup_prompts(data_with_awards)
    assert len(prompts[0]["system"]) > 100
    assert "fantasy football" in prompts[0]["system"].lower()
