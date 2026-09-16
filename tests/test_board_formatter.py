import pytest

from src.awards_engine import compute_awards
from src.board_formatter import format_for_board
from tests.fixtures.sample_weekly_data import SAMPLE_WEEK

MATCHUP_HTML = (
    '<div class="matchup-subtitle">A Mercy Rule Would Have Been Kinder</div>'
    '<div class="winner-paragraph">Alice dominated with Mahomes going off.</div>'
    '<div class="loser-paragraph">Bob had a rough week, benched the wrong RB.</div>'
    '<div class="play-of-week">Mahomes threw for 38.2 points.</div>'
)

AWARDS_HTML = (
    '<div class="award-block">Dumpster Fire: Hank scored 72.3, lowest of the week.</div>'
    '<div class="award-block">Glass Cannon: Alice scored 148.6, highest of the week.</div>'
    '<div class="season-leaderboard">Alice leads with 3 total awards.</div>'
)

ASSEMBLY_HTML = (
    '<div class="cold-open">Week 5 had it all.</div>'
    '<div class="power-rankings">Alice sits atop the standings undefeated.</div>'
    '<div class="waiver-whisper">Someone streamed a defense and it worked.</div>'
    '<div class="matchup-of-week">Alpha Dogs vs Touchdown Bandits should be a banger.</div>'
    '<div class="turd-matchup">Benchwarmer FC vs Dumpster Fire nobody wants to watch.</div>'
    '<div class="threat-board-rest">Other matchups exist too.</div>'
    '<div class="sign-off">See you next week.</div>'
)


@pytest.fixture
def data():
    d = SAMPLE_WEEK
    d.awards = compute_awards(d)
    return d


def test_board_text_contains_no_html_tags(data):
    matchup_outputs = [MATCHUP_HTML] * len(data.matchups)
    text = format_for_board(data, matchup_outputs, AWARDS_HTML, ASSEMBLY_HTML)
    assert "<div" not in text
    assert "</div>" not in text
    assert 'class="' not in text


def test_board_text_contains_scores_and_team_names(data):
    matchup_outputs = [MATCHUP_HTML] * len(data.matchups)
    text = format_for_board(data, matchup_outputs, AWARDS_HTML, ASSEMBLY_HTML)
    assert "Alpha Dogs" in text
    assert "148.6" in text
    assert "Benchwarmer FC" in text


def test_board_text_contains_matchup_of_week_and_turd(data):
    matchup_outputs = [MATCHUP_HTML] * len(data.matchups)
    text = format_for_board(data, matchup_outputs, AWARDS_HTML, ASSEMBLY_HTML)
    assert "MATCHUP OF THE WEEK" in text
    assert "TURD OF THE WEEK" in text


def test_board_text_contains_awards_section(data):
    matchup_outputs = [MATCHUP_HTML] * len(data.matchups)
    text = format_for_board(data, matchup_outputs, AWARDS_HTML, ASSEMBLY_HTML)
    assert "WEEKLY AWARDS" in text
    assert "Dumpster Fire" in text
    assert "3 total awards" in text


def test_board_text_has_no_excessive_blank_lines(data):
    matchup_outputs = [MATCHUP_HTML] * len(data.matchups)
    text = format_for_board(data, matchup_outputs, AWARDS_HTML, ASSEMBLY_HTML)
    assert "\n\n\n" not in text
