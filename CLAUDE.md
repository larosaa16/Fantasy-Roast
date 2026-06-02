# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Fantasy-Roast** generates and emails a weekly Fantasy Football roast to a Yahoo Fantasy league. It fetches matchup data via the Yahoo Fantasy API (yfpy), computes awards in pure Python, then makes 6–9 Claude API calls to generate creative roast copy, and sends it as an HTML email every Tuesday.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (no live API needed)
pytest tests/ -v

# Run a single test file
pytest tests/test_awards_engine.py -v

# Preview generated email in browser (saves to output/week_N_preview.html)
python main.py --week 5 --preview

# Print email HTML to stdout without sending
python main.py --week 5 --dry-run

# Generate and send
python main.py --week 5

# First-time Yahoo OAuth setup
python main.py --auth
```

## Architecture

The pipeline runs in strict order — each stage's output feeds the next:

```
fetch_weekly_data()        → WeeklyData
compute_awards()           → AwardResults (attached to WeeklyData)
update_awards_history()    → writes data/awards_history.json
build_matchup_prompts()    → one Claude call per matchup (4–7 calls)
build_awards_prompt()      → one Claude call for awards + season leaderboard
build_assembly_prompt()    → one Claude call for cold open, power rankings,
                             waiver whisper, threat board, sign-off
assemble_email()           → final HTML via Jinja2
send_roast_email()         → Gmail SMTP
```

### Key Files

- `src/models.py` — all dataclasses (`WeeklyData`, `Matchup`, `TeamSnapshot`, `PlayerResult`, `AwardResults`)
- `src/awards_engine.py` — pure Python award logic; also owns `data/awards_history.json` season tracking
- `src/prompt_builder.py` — builds all three Claude prompt types; loads `league_config.json` for lore injection
- `src/claude_client.py` — single `call()` function with exponential backoff retry; model set to `claude-opus-4-7`
- `src/data_fetcher.py` — yfpy wrapper that normalizes raw Yahoo API responses into `WeeklyData`
- `src/email_assembler.py` — parses Claude's HTML fragment output by CSS class, renders Jinja2 template
- `templates/roast_email.html` — single-column dark sports-newsletter design; all styles inline for Gmail

### Claude Output Contract

Claude is always prompted to return **HTML fragments with specific CSS classes**, not full HTML documents. `email_assembler.py` extracts them via regex on class names:

| CSS class | Content |
|---|---|
| `matchup-subtitle` | 5-8 word punchy subtitle |
| `winner-paragraph` | 2-3 sentence winner praise |
| `loser-paragraph` | 3-4 sentence roast, commiserating close |
| `play-of-week` | 1-2 sentence standout player callout |
| `award-block` | Per-award ceremony copy |
| `season-leaderboard` | HTML table of cumulative award totals |
| `cold-open` | 3-5 sentence weekly intro |
| `power-rankings` | ~100 word standings narrative |
| `waiver-whisper` | 2-4 sentence dramatic player commentary |
| `matchup-of-week` | 2-3 sentence top matchup preview |
| `turd-matchup` | 2-3 sentence worst matchup roast |
| `threat-board-rest` | One-liner per remaining matchup |
| `sign-off` | 1-2 sentence closer |

If Claude doesn't wrap output in a div with the expected class, `_extract()` falls back to returning the raw stripped text.

### Award Logic (`awards_engine.py`)

Awards are computed before any Claude calls, from raw scores only:

| Award | Criteria |
|---|---|
| Dumpster Fire | Lowest score of the week |
| Glass Cannon | Highest score of the week |
| Bench Mogul | Largest gap: `best_possible_score - actual_score` |
| Lucky Rabbit | Winner whose score ranks in the bottom half of all teams |
| Heartbreak Hotel | Closest losing margin |
| Manager Spotlight | Any starter who scored ≥1.5× their projection AND ≥20 pts |

Season history in `data/awards_history.json` is append-only per week — re-running the same week number is idempotent.

### League Lore (`league_config.json`)

Nicknames, running jokes, and traditions in `league_config.json` are injected into the system prompt on every Claude call via `prompt_builder._build_system_prompt()`. Update this file to shape the roast voice over time.

## Configuration

Copy `.env.example` to `.env`. Required vars: `YAHOO_CLIENT_ID`, `YAHOO_CLIENT_SECRET`, `YAHOO_LEAGUE_ID`, `ANTHROPIC_API_KEY`, `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECIPIENTS`.

Yahoo OAuth token is saved to `data/token.json` after running `--auth`. Do not commit this file.
