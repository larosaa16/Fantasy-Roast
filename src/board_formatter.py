"""
Formats the weekly roast as plain text for manual copy-paste into the
Yahoo league message board (Yahoo's API has no endpoint to post there,
and boards don't render HTML/CSS, so this produces a clean plain-text
version of the same content instead).
"""

import html
import re

from src.email_assembler import _extract
from src.models import WeeklyData


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def _strip_award_blocks(awards_html: str) -> str:
    # Insert paragraph breaks before each award/leaderboard div so stripped
    # tags don't run every award together into one wall of text.
    spaced = re.sub(r'<div class="(award-block|season-leaderboard)">', r"\n\n", awards_html)
    cleaned = _clean(spaced)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def format_for_board(
    data: WeeklyData,
    matchup_outputs: list[str],
    awards_output: str,
    assembly_output: str,
) -> str:
    lines: list[str] = []

    lines.append(f"🔥 THE WEEKLY ROAST — WEEK {data.week_number} 🔥")
    lines.append(data.league_name)
    lines.append("=" * 50)
    lines.append("")
    lines.append(_clean(_extract(assembly_output, "cold-open")))
    lines.append("")

    lines.append("🏈 THIS WEEK'S MATCHUPS")
    lines.append("-" * 50)
    for m, raw in zip(data.matchups, matchup_outputs):
        lines.append("")
        lines.append(f"{m.winner.team_name} {m.winner.score} — {m.loser.team_name} {m.loser.score}")
        subtitle = _clean(_extract(raw, "matchup-subtitle"))
        if subtitle:
            lines.append(f"\"{subtitle}\"")
        lines.append("")
        lines.append(_clean(_extract(raw, "winner-paragraph")))
        lines.append("")
        lines.append(_clean(_extract(raw, "loser-paragraph")))
        play = _clean(_extract(raw, "play-of-week"))
        if play:
            lines.append("")
            lines.append(f"⭐ Play of the Week: {play}")
        lines.append("")
        lines.append("-" * 50)

    lines.append("")
    lines.append("🏆 WEEKLY AWARDS")
    lines.append("-" * 50)
    lines.append("")
    lines.append(_strip_award_blocks(awards_output))
    lines.append("")

    power = _clean(_extract(assembly_output, "power-rankings"))
    if power:
        lines.append("📊 POWER RANKINGS DISPATCH")
        lines.append("-" * 50)
        lines.append(power)
        lines.append("")

    whisper = _clean(_extract(assembly_output, "waiver-whisper"))
    if whisper:
        lines.append("⚡ WAIVER WIRE WHISPER")
        lines.append("-" * 50)
        lines.append(whisper)
        lines.append("")

    lines.append("🎯 NEXT WEEK'S THREAT BOARD")
    lines.append("-" * 50)
    mow = _clean(_extract(assembly_output, "matchup-of-week"))
    if mow:
        lines.append("")
        lines.append("🔥 MATCHUP OF THE WEEK")
        lines.append(mow)
    turd = _clean(_extract(assembly_output, "turd-matchup"))
    if turd:
        lines.append("")
        lines.append("💩 TURD OF THE WEEK")
        lines.append(turd)
    rest = _clean(_extract(assembly_output, "threat-board-rest"))
    if rest:
        lines.append("")
        lines.append(rest)
    lines.append("")

    sign_off = _clean(_extract(assembly_output, "sign-off"))
    if sign_off:
        lines.append("=" * 50)
        lines.append(sign_off)

    return "\n".join(lines)
