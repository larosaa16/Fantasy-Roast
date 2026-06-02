"""
Entry point. Run modes:
  python main.py --week 5              # fetch, generate, send
  python main.py --week 5 --dry-run    # fetch, generate, print HTML to stdout
  python main.py --week 5 --preview    # fetch, generate, save to output/preview.html
  python main.py --auth                # run Yahoo OAuth flow and save token
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _require_env(*keys: str) -> None:
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in the values.")
        sys.exit(1)


def run_auth() -> None:
    from src.data_fetcher import _make_query
    print("Starting Yahoo OAuth flow...")
    query = _make_query()
    query.get_current_user()
    print("Authentication successful. Token saved to data/token.json")


def run_roast(week: int, dry_run: bool = False, preview: bool = False) -> None:
    _require_env("YAHOO_CLIENT_ID", "YAHOO_CLIENT_SECRET", "YAHOO_LEAGUE_ID", "ANTHROPIC_API_KEY")
    if not dry_run and not preview:
        _require_env("EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECIPIENTS")

    from src.awards_engine import compute_awards, load_awards_history, update_awards_history
    from src.claude_client import call_prompt
    from src.data_fetcher import fetch_weekly_data
    from src.email_assembler import assemble_email
    from src.email_sender import send_roast_email
    from src.prompt_builder import build_assembly_prompt, build_awards_prompt, build_matchup_prompts

    print(f"Fetching Week {week} data from Yahoo...")
    data = fetch_weekly_data(week=week)

    print("Computing awards...")
    data.awards = compute_awards(data)
    history = update_awards_history(week, data.awards, data.season)

    print(f"Generating matchup roasts ({len(data.matchups)} matchups)...")
    matchup_prompts = build_matchup_prompts(data)
    matchup_outputs = []
    for i, prompt in enumerate(matchup_prompts, 1):
        print(f"  Matchup {i}/{len(matchup_prompts)}: {prompt['matchup'].winner.team_name} vs {prompt['matchup'].loser.team_name}")
        matchup_outputs.append(call_prompt(prompt))

    print("Generating awards ceremony...")
    awards_output = call_prompt(build_awards_prompt(data, history))

    print("Generating cold open, power rankings, and threat board...")
    assembly_output = call_prompt(
        build_assembly_prompt(data, matchup_outputs, awards_output)
    )

    print("Assembling email...")
    html = assemble_email(data, matchup_outputs, awards_output, assembly_output)

    if dry_run:
        print("\n" + "=" * 60)
        print(html)
        return

    if preview:
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"week_{week}_preview.html"
        out_path.write_text(html)
        print(f"Preview saved to {out_path}")
        return

    print("Sending email...")
    send_roast_email(html, week=week, league_name=data.league_name)
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fantasy Football Roast Generator")
    parser.add_argument("--week", type=int, help="NFL week number to roast")
    parser.add_argument("--dry-run", action="store_true", help="Print HTML to stdout, don't send")
    parser.add_argument("--preview", action="store_true", help="Save HTML to output/week_N_preview.html")
    parser.add_argument("--auth", action="store_true", help="Run Yahoo OAuth setup")
    args = parser.parse_args()

    if args.auth:
        run_auth()
    elif args.week:
        run_roast(week=args.week, dry_run=args.dry_run, preview=args.preview)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
