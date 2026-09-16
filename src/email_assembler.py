"""
Parses Claude HTML fragment outputs and merges them into the Jinja2 email template.
"""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.models import Matchup, WeeklyData

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def _extract(html: str, css_class: str, default: str = "") -> str:
    pattern = rf'<div class="{css_class}">(.*?)</div>'
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: if the Claude output doesn't wrap in a div, return stripped text
    return html.strip() or default


def assemble_email(
    data: WeeklyData,
    matchup_outputs: list[str],
    awards_output: str,
    assembly_output: str,
) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    template = env.get_template("roast_email.html")

    matchup_blocks = []
    for i, (m, raw) in enumerate(zip(data.matchups, matchup_outputs)):
        matchup_blocks.append({
            "winner_name": m.winner.team_name,
            "winner_score": m.winner.score,
            "loser_name": m.loser.team_name,
            "loser_score": m.loser.score,
            "subtitle": _extract(raw, "matchup-subtitle"),
            "winner_paragraph": _extract(raw, "winner-paragraph"),
            "loser_paragraph": _extract(raw, "loser-paragraph"),
            "play_of_week": _extract(raw, "play-of-week"),
        })

    return template.render(
        week_number=data.week_number,
        league_name=data.league_name,
        season=data.season,
        matchups=matchup_blocks,
        awards_html=awards_output,
        cold_open=_extract(assembly_output, "cold-open"),
        power_rankings=_extract(assembly_output, "power-rankings"),
        waiver_whisper=_extract(assembly_output, "waiver-whisper"),
        matchup_of_week=_extract(assembly_output, "matchup-of-week"),
        turd_matchup=_extract(assembly_output, "turd-matchup"),
        threat_board_rest=_extract(assembly_output, "threat-board-rest"),
        sign_off=_extract(assembly_output, "sign-off"),
    )
