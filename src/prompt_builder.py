"""
Builds all Claude API prompt payloads from WeeklyData + league_config.json.
Returns ready-to-send message dicts; no API calls happen here.
"""

import json
from pathlib import Path

from src.models import AwardResults, Matchup, TeamSnapshot, WeeklyData

CONFIG_PATH = Path(__file__).parent.parent / "league_config.json"

SYSTEM_PROMPT = """You are the official roast writer for a fantasy football league. \
Your job is to write the weekly roast email that goes out every Tuesday morning to all league members.

TONE RULES:
- Funny and playful — medium heat. Points sting slightly, then make the loser laugh.
- Use real names, real scores, real margins — specificity is the source of every good joke.
- Never mean-spirited beyond fantasy performance. Never personal. Never profane.
- Mix mock-formal language with casual banter for contrast.
- Short sentences land punchlines. Long sentences build setup.
- Fantasy football jargon is encouraged: "left points on the bench," "streaming a defense," etc.
- Pop culture references should be broadly recognizable, not niche.
- Losers always end on a commiserating note, not a devastating one.
- Winners get praised, but deflate slightly if the win was lucky.

FORMAT RULES:
- Return clean HTML fragments only — no full HTML document wrapper.
- Use exact player names, team names, and scores from the data provided.
- Do not editorialize about real NFL players' careers or personal lives.
{lore_block}
PERSONA: {persona}"""


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def _build_system_prompt() -> str:
    cfg = _load_config()
    lore_lines = []
    if cfg.get("nicknames"):
        nicks = ", ".join(f"{k} = '{v}'" for k, v in cfg["nicknames"].items())
        lore_lines.append(f"MANAGER NICKNAMES (use these in the copy): {nicks}")
    if cfg.get("running_jokes"):
        jokes = "; ".join(cfg["running_jokes"])
        lore_lines.append(f"RUNNING LEAGUE JOKES (weave in where natural): {jokes}")
    if cfg.get("traditions"):
        traditions = "; ".join(cfg["traditions"])
        lore_lines.append(f"LEAGUE TRADITIONS (reference if relevant): {traditions}")

    lore_block = ("\n" + "\n".join(lore_lines) + "\n") if lore_lines else ""
    persona = cfg.get("roast_persona", "Your Commissioner's Robot")
    return SYSTEM_PROMPT.format(lore_block=lore_block, persona=persona)


def _format_team(team: TeamSnapshot) -> str:
    lines = [f"  Record entering week: {team.wins}-{team.losses}"]
    if team.starters:
        lines.append("  Starters:")
        for p in team.starters:
            lines.append(
                f"    {p.name} ({p.position}): {p.actual_points} pts (projected: {p.projected_points})"
            )
    if team.bench:
        lines.append("  Bench:")
        for p in team.bench:
            lines.append(
                f"    {p.name} ({p.position}): {p.actual_points} pts (projected: {p.projected_points})"
            )
    if team.best_possible_score > team.score:
        lines.append(
            f"  Best possible score (best-ball): {team.best_possible_score} pts"
        )
    return "\n".join(lines)


def build_matchup_prompts(data: WeeklyData) -> list[dict]:
    system = _build_system_prompt()
    prompts = []
    for m in data.matchups:
        user_msg = f"""Write the matchup block for Week {data.week_number} of the {data.league_name} roast email.

MATCHUP:
Winner: {m.winner.team_name} ({m.winner.manager_name}) — {m.winner.score} pts
Loser:  {m.loser.team_name} ({m.loser.manager_name}) — {m.loser.score} pts
Margin: {m.margin} pts

WINNER'S ROSTER:
{_format_team(m.winner)}

LOSER'S ROSTER:
{_format_team(m.loser)}

Produce the following as HTML fragments with these exact CSS classes:
1. <div class="matchup-subtitle"> — a punchy 5-8 word subtitle for this matchup
2. <div class="winner-paragraph"> — 2-3 sentences celebrating the winner (deflate slightly if lucky win)
3. <div class="loser-paragraph"> — 3-4 sentences roasting the loser; end commiserating not crushing
4. <div class="play-of-week"> — 1-2 sentences on the single most notable player performance in this matchup"""

        prompts.append({
            "system": system,
            "messages": [{"role": "user", "content": user_msg}],
            "matchup": m,
        })
    return prompts


def build_awards_prompt(data: WeeklyData, history: dict) -> dict:
    awards = data.awards
    system = _build_system_prompt()

    def _fmt_award(label: str, stat: str) -> str:
        return f"- {label}: {stat}"

    lines = [
        f"Write the Weekly Awards Ceremony section for Week {data.week_number} of the {data.league_name} roast.",
        "",
        "AWARD DATA:",
        _fmt_award("🔥 Dumpster Fire Award", awards.dumpster_fire.stat_line + f" — {awards.dumpster_fire.team_name}"),
        _fmt_award("💥 Glass Cannon Award", awards.glass_cannon.stat_line + f" — {awards.glass_cannon.team_name}"),
        _fmt_award("🎯 Bench Mogul Award", awards.bench_mogul.stat_line + f" — {awards.bench_mogul.team_name}"),
    ]
    if awards.lucky_rabbit:
        lines.append(_fmt_award("🐇 Lucky Rabbit Award", awards.lucky_rabbit.stat_line + f" — {awards.lucky_rabbit.team_name}"))
    if awards.heartbreak_hotel:
        lines.append(_fmt_award("💔 Heartbreak Hotel Award", awards.heartbreak_hotel.stat_line + f" — {awards.heartbreak_hotel.team_name}"))
    if awards.manager_spotlight:
        for s in awards.manager_spotlight:
            lines.append(_fmt_award("⭐ Manager Spotlight", s.stat_line + f" — {s.team_name}"))

    # Season leaderboard
    totals = history.get("totals", {})
    if totals:
        lines += ["", "SEASON AWARD LEADERBOARD (include this as a table in the section):"]
        sorted_teams = sorted(totals.items(), key=lambda x: x[1].get("total", 0), reverse=True)
        for team, counts in sorted_teams:
            detail = ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in counts.items() if k != "total")
            lines.append(f"  {team} — {counts.get('total', 0)} total awards ({detail})")

    lines += [
        "",
        "For each award: write the award title, a one-line stat callout, and 2-3 sentences of roast/celebration copy.",
        "Use mock-formal trophy-ceremony language.",
        "For the Manager Spotlight, celebrate the smart roster decision warmly.",
        "End with a Season Award Leaderboard as an HTML table showing cumulative award counts.",
        "",
        "Return as HTML fragments. Each award in <div class='award-block'>. Leaderboard in <div class='season-leaderboard'>.",
    ]

    return {
        "system": system,
        "messages": [{"role": "user", "content": "\n".join(lines)}],
    }


def build_assembly_prompt(
    data: WeeklyData,
    matchup_outputs: list[str],
    awards_output: str,
) -> dict:
    system = _build_system_prompt()

    standings_lines = []
    for s in data.standings:
        standings_lines.append(
            f"  {s.team_name} ({s.manager_name}): {s.wins}-{s.losses}, "
            f"{s.points_for} PF, {s.points_against} PA"
        )

    next_week_lines = [f"  {a} vs {b}" for a, b in data.next_week_matchups]

    matchup_text = "\n\n---\n\n".join(matchup_outputs)

    user_msg = f"""Assemble the final connective tissue for the Week {data.week_number} {data.league_name} roast email.

Using the matchup blocks and awards below as source material, write:

1. <div class="cold-open"> — 3-5 sentence punchy intro referencing the most dramatic moment of the week. Tease what's inside.

2. <div class="power-rankings"> — ~100 words of narrative standings commentary. Backhanded compliment to the leader. Mock concern for anyone on a losing streak. Underdog hype if applicable.
CURRENT STANDINGS:
{chr(10).join(standings_lines)}

3. <div class="waiver-whisper"> — 2-4 sentences of overly-dramatic sports-analyst insider commentary on a player who exploded or imploded this week. Reference real names from the matchup data.

4. THREAT BOARD for next week — three distinct items:
   a. <div class="matchup-of-week"> — Pick the most exciting upcoming matchup (highest combined wins or most interesting rivalry). Write it up as a boxing promoter hyping the main event. 2-3 sentences.
   b. <div class="turd-matchup"> — Pick the worst upcoming matchup (lowest combined wins or most boring). Roast it mercilessly in 2-3 sentences. Make it funny, not mean.
   c. <div class="threat-board-rest"> — For each remaining matchup, one boxing-promoter one-liner. Format as an HTML list.
NEXT WEEK'S MATCHUPS:
{chr(10).join(next_week_lines)}

5. <div class="sign-off"> — 1-2 sentence sign-off. Signed as the league persona.

EXISTING CONTENT FOR CONTEXT (reference and callback to these for continuity):
--- MATCHUP BLOCKS ---
{matchup_text}

--- AWARDS ---
{awards_output}"""

    return {
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }
