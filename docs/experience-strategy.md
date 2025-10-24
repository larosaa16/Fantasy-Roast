# Fantasy Roast Experience Strategy

This document captures working decisions for the Fantasy Roast control room so that future features stay coherent and fun.

## 1. Sleeper Integration

### How do we connect the Sleeper API to automatically pull league data?
- Use the existing `SleeperLeagueConnector` in `src/platforms/sleeper/connector.js` as the transport layer.
- Add a scheduled job (e.g. `setInterval` or a cron runner) that hydrates league state once an hour during the season.
- Cache the raw responses in Supabase (or an in-memory store such as Redis when hosted) keyed by `leagueId:week` so the UI can load instantly.
- Expose a `/api/leagues/sleeper/:leagueId/snapshot` endpoint that returns the cached structure and triggers a background refresh when stale (>10 minutes old).

### Do we want to generate roasts for every team or just matchups of the week?
- Default to **matchups of the week** so the UI spotlights the most dramatic clashes.
- Provide a toggle in the UI that lets commissioners switch to "league sweep" mode, which loops through every matchup and queues roast requests sequentially to stay within rate limits.

### How should the app decide who to roast harder?
- Compute three scores per matchup: lowest total score, biggest margin of defeat, and worst lineup decision (bench points lost versus starter).
- Normalize the scores to 0-1 and feed the largest value into the roast prompt as the "spice multiplier." The UI can surface the leading reason (e.g. "biggest blowout") to explain the intensity.

## 2. Roast Logic

### Should spice level adjust automatically based on record or score difference?
- Yes. Base spice on score difference, then add ±10% for record disparity (piling on upset losses, easing up on underdogs).
- Manual override remains available through the tone slider so commissioners can tone things down when needed.

### Do we want the roast tone to change weekly?
- Introduce a weekly theme system driven by presets ("Rival Week," "Midseason Breakdown," playoffs, etc.).
- Store the active theme in Supabase so multiple admins share the same context. The UI shows the current theme and allows future scheduling.

### Should we store past roasts?
- Yes. Persist every roast with matchup metadata plus prompt inputs in Supabase. This unlocks: avoiding repeated jokes, tracking improvement, and generating seasonal recaps.

## 3. Formatting

### How should the output be formatted?
- Generate Markdown by default so content is ready for Discord/Slack drops.
- When serving inside the control room, render Markdown to HTML client-side using a trusted parser (e.g. `marked`) to keep the UI consistent.

### Do we want to include emojis, logos, or stats?
- Allow optional embellishments:
  - League-wide default emoji palette and per-team emoji overrides stored in Supabase.
  - Show league logo (if supplied) in the UI header and include image links in exported Markdown when available.
  - Embed top-line stats (highest scorer, bench points) in a concise table after the roast paragraph.

### Should each roast include a highlight and shame section?
- Yes. Template the response prompt with two dedicated sections:
  - **Highlight Reel** – celebrate the best-performing player or clutch move.
  - **Walk of Shame** – call out the worst decision or underperformer.

## 4. Data Handling & Operations

### Storage
- Store every generated roast in Supabase and mirror weekly exports to `/out/week_<number>.md` for human-friendly archives.
- Maintain a `roasts_history.json` aggregate that the UI can load for analytics and streak tracking.
- Tag entries with `platform`, `leagueId`, `week`, `matchupId`, and `teamIds` to make queries trivial.

### Config
- Keep sensitive or frequently tweaked values in `.env`: `LEAGUE_ID`, default `ROAST_SPICE`, default `OPENAI_MODEL`.
- Support multiple leagues by allowing comma-separated `LEAGUE_IDS` and surfacing them in the UI dropdown.

### Error Handling
- When a team is missing stats (bye weeks, postponed games), mark the matchup as `pending` and skip roast generation until both teams have complete data.
- Wrap OpenAI calls with retries (exponential backoff up to three attempts) and persist failures with diagnostic info so admins can manually retry from the UI.
- Surface clear toast notifications in the UI for both recoverable and fatal errors, and log structured errors server-side for observability.

## 5. Automation

### Should the script auto-run every Tuesday morning to roast the week’s results?
- Yes. Schedule a hosted cron (Supabase Edge Function cron or GitHub Actions scheduled workflow) for **Tuesdays at 09:00 local league time** so box scores have settled. The job pulls the latest Sleeper snapshots and queues roast generation for the selected league(s).

### Do we want it to open a GitHub PR with the new `roasts/week_X.md` file automatically?
- Automate the archival path: the weekly job writes `/out/week_<number>.md` and commits it on a `roast/week-<number>` branch, then opens a PR tagged for review. Human approval keeps the tone in check while still providing one-click publishing.

### Should we also post it straight to Discord or email the league?
- Provide optional integrations controlled by environment flags (`DISCORD_WEBHOOK_URL`, `SMTP_*`). When configured, the automation posts the Markdown digest to Discord and emails a nicely formatted HTML summary. Defaults stay off so private leagues opt in explicitly.

### Do we want GitHub Actions to handle running the roast job on push?
- Keep CI focused on validation (lint, type checks, smoke tests). Reserve scheduled or manual dispatch workflows for running the heavy roast generation so production API keys are not exposed during every push.

### Should it lint or test before merging (e.g., check JSON validity, API key existence)?
- Add a GitHub Actions workflow that runs:
  - `npm test` (future unit tests) and JSON schema validation for `/out` exports.
  - A configuration sanity check ensuring required secrets (`OPENAI_API_KEY`, `SUPABASE_*`) are present before executing automation jobs.

## 6. Interface & Expansion

### Do we want a simple Streamlit or Flask interface to pick a team/week and generate on demand?
- Stick with the existing vanilla UI for now; when expanding, build a lightweight web dashboard (Next.js or Remix) so we can reuse shared components and host static exports. Streamlit/Flask are nice for prototypes but add Python infrastructure overhead.

### Should we add a leaderboard or “Roast Hall of Fame”?
- Yes. Use the stored roast history to power a "Hall of Flame" tab ranking:
  - Spiciest burn (highest spice multiplier).
  - Biggest blowout margin.
  - Most improved manager week-over-week.
  The UI surfaces badges and links back to the original write-up.

### Would we let users upload their Sleeper league ID and get roasts on a hosted site?
- Offer a **hosted guest mode** where visitors supply a Sleeper league ID. Requests run in a rate-limited queue, and results are ephemeral unless the commissioner signs in. This keeps onboarding low-friction without storing stranger data indefinitely.

### Should we add login/auth if we ever publish it?
- Yes. Implement Supabase Auth with magic links for commissioners. Auth gates permanent storage, automation settings, and Discord/email hooks, while public visitors retain read-only access to published recaps.

## 7. Prompt Optimization

### Should we feed the model last week’s roast as context to keep continuity?
- Provide the last matchup’s roast and key stats as contextual memory when available. Limit to ~1,000 tokens to avoid blowing up costs, and fall back gracefully when history is missing.

### Should the tone differ by team’s record?
- Blend record into the spice multiplier: undefeated teams receive confident jabs, while winless teams get empathetic humor. Encode this as descriptive metadata in the system prompt so tone remains consistent.

### Do we want a JSON schema to structure the roast (e.g., intro / punchline / outro)?
- Yes. Request a JSON object with `intro`, `praise`, `roast`, `highlight`, and `shame` fields. This guarantees predictable formatting for Markdown and downstream exports.

### Should we test gpt-5-mini vs gpt-5 for cost vs quality?
- Run A/B tests on archived matchups: generate drafts with `gpt-5-mini` (cost saver) and `gpt-5` (premium) using identical prompts. Collect feedback scores from commissioners in the UI to inform the default model per league.

### Do we want deterministic outputs (temperature=0.3) or variety (temperature=0.8)?
- Default to moderate creativity (`temperature=0.6`, `top_p=0.9`) so roasts feel fresh yet coherent. Allow commissioners to override per request, and have automation use the league default for consistency.
