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
