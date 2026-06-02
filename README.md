# Fantasy-Roast 🏈🔥

Automatically generates and emails a weekly Fantasy Football roast to your Yahoo league — recapping matchups, roasting the losers, celebrating smart managers, and previewing the upcoming week. Powered by Claude AI.

---

## What It Sends Every Tuesday

- **Matchup breakdowns** — winner praise + loser roast for every game, with a Play of the Week callout
- **Manager Spotlight** — celebrates whoever made the best roster decisions
- **Weekly Awards** — Dumpster Fire, Glass Cannon, Bench Mogul, Lucky Rabbit, Heartbreak Hotel
- **Season Award Leaderboard** — running totals so the shame compounds week over week
- **Power Rankings** — narrative standings commentary
- **Threat Board** — next week preview including Matchup of the Week and Turd of the Week

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Yahoo Developer App

1. Go to [developer.yahoo.com](https://developer.yahoo.com/apps/) and sign in
2. Click **Create an App**
3. Set the app name to anything (e.g. "Fantasy Roast")
4. Set **Redirect URI** to `oob` (out-of-band, for desktop apps)
5. Under **API Permissions**, select **Fantasy Sports** → **Read/Write**
6. Click **Create App**
7. Copy your **Client ID** and **Client Secret**

### 3. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```
YAHOO_CLIENT_ID=        # from step 2
YAHOO_CLIENT_SECRET=    # from step 2
YAHOO_LEAGUE_ID=        # your Yahoo league ID (found in the league URL)
YAHOO_GAME_CODE=nfl

ANTHROPIC_API_KEY=      # from console.anthropic.com

EMAIL_SENDER=           # your Gmail address
EMAIL_PASSWORD=         # Gmail App Password (not your regular password — see note below)
EMAIL_RECIPIENTS=       # comma-separated email addresses for the whole league
```

> **Gmail App Password**: Go to your Google Account → Security → 2-Step Verification → App passwords. Generate one for "Mail".

### 4. Find your Yahoo League ID

Open your Yahoo Fantasy league in a browser. The URL looks like:
`https://football.fantasysports.yahoo.com/f1/XXXXXX`

The number at the end (`XXXXXX`) is your League ID.

### 5. Authenticate with Yahoo (first time only)

```bash
python main.py --auth
```

This opens a Yahoo login page in your browser, asks you to approve access, then gives you a verification code to paste back in the terminal. The token is saved to `data/token.json` and auto-refreshes after that.

### 6. Add your league's personality

Open `league_config.json` and fill in nicknames, inside jokes, and traditions. Claude will weave these into the roasts each week.

---

## Running the Roast

```bash
# Preview the email in your browser (no email sent)
python main.py --week 5 --preview
# Output saved to output/week_5_preview.html

# Print the HTML to your terminal (no email sent)
python main.py --week 5 --dry-run

# Generate and send
python main.py --week 5
```

Replace `5` with the current NFL week number.

---

## Automating Weekly Sends

Add a cron job to run every Tuesday morning after Monday Night Football finishes:

```bash
crontab -e
```

Add this line (runs at 6 AM every Tuesday):
```
0 6 * * 2 cd /path/to/Fantasy-Roast && python main.py --week $(date +\%W)
```

> Note: `date +%W` returns the ISO week number, which may be off by 1 from NFL week numbers depending on the season start. Adjust the offset as needed.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover award logic and prompt building against fixture data — no live API calls needed.

---

## File Structure

```
src/
  data_fetcher.py      # Yahoo API → WeeklyData
  awards_engine.py     # Computes awards + tracks season history
  prompt_builder.py    # Builds Claude prompts from WeeklyData
  claude_client.py     # Anthropic API calls with retry
  email_assembler.py   # Merges Claude output into HTML template
  email_sender.py      # Gmail SMTP sending
templates/
  roast_email.html     # Jinja2 HTML email template
data/
  awards_history.json  # Season-long award totals (auto-updated each week)
  token.json           # Yahoo OAuth token (created by --auth, don't commit)
league_config.json     # Your league's nicknames, jokes, and traditions
```
