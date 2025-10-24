# Fantasy Roast Control Room

A zero-dependency Node.js server that serves the dark-mode Fantasy Roast control room UI, fetches fantasy football matchups, asks OpenAI for witty praise and roasts, and persists results to Supabase. Everything runs on modern Node 18+ APIs—no `npm install` required.

## Features

- 🔌 **Platform connectors** with a production-ready Sleeper integration and scaffolding for Yahoo and ESPN.
- 🤖 **OpenAI-powered banter** that celebrates winners and lightly roasts the losers based on matchup data.
- 🗄️ **Supabase persistence** via the REST interface for storing generated roasts.
- 🖥️ **Built-in UI** served from the same server for managing lookups and roast generation.

## Prerequisites

- Node.js 18.19 or newer (for `fetch`, `URL`, and `node --watch`).
- OpenAI API key with access to the Responses API.
- Supabase project with a `roasts` table (schema below).

## Setup

1. Copy the example environment file and provide your credentials:

   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `PORT` | Port used by the HTTP server (defaults to `3000`). |
   | `OPENAI_API_KEY` | API key for the OpenAI Responses API. |
   | `SUPABASE_URL` | Supabase project URL (without the trailing slash). |
   | `SUPABASE_ANON_KEY` | Supabase anon/public API key with insert permission on `roasts`. |

2. Create the `roasts` table if it does not exist:

   ```sql
   create table if not exists public.roasts (
     id uuid primary key default gen_random_uuid(),
     created_at timestamptz not null default now(),
     matchup_id text not null,
     league_id text not null,
     platform text not null,
     week int not null,
     winner_id text not null,
     loser_id text not null,
     praise text not null,
     roast text not null
   );
   ```

3. Start the development server (hot reloading with `node --watch` requires Node 18.11+):

   ```bash
   npm run dev
   ```

   The UI and API will be available at `http://localhost:3000`.

## API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Liveness probe for health checks. |
| `GET` | `/api/leagues/:platform/:leagueId/matchups?week=1` | Fetch weekly matchups from a fantasy platform. |
| `POST` | `/api/leagues/:platform/:leagueId/roast` | Generate and persist a roast for a specific matchup. |

### Example: Generate a roast

```bash
curl -X POST http://localhost:3000/api/leagues/sleeper/12345/roast \
  -H "Content-Type: application/json" \
  -d '{
    "matchup": {
      "id": "12345-1-4",
      "week": 1,
      "leagueId": "12345",
      "platform": "sleeper",
      "teams": [
        {
          "teamId": "111",
          "teamName": "Smash Bros",
          "manager": { "id": "abc", "displayName": "Alex" },
          "points": 134.6,
          "players": []
        },
        {
          "teamId": "222",
          "teamName": "Bye Week",
          "manager": { "id": "def", "displayName": "Jordan" },
          "points": 97.3,
          "players": []
        }
      ]
    }
  }'
```

## Project Structure

```
src/
├── config/           # Environment management
├── domain/           # Shared JSDoc typedefs for matchups/roasts
├── http/             # Lightweight router and request handlers
├── platforms/        # Platform-specific connectors and mappers
├── services/         # Business logic (matchups, roasts, Supabase)
└── utils/            # Cross-cutting helpers (logger)
public/               # Dark-mode control room UI assets
```

## Roadmap

- [ ] Complete Yahoo Fantasy Sports OAuth flow and data mappers.
- [ ] Reverse-engineer ESPN private endpoints or integrate with a partner API.
- [ ] Add scheduled jobs to auto-generate weekly roasts.
- [ ] Expand Supabase schema with league/user metadata and analytics.

## Experience Enhancements

Here are a few playful feature ideas to make the control room even more entertaining:

1. 🎚️ **Roast tone dial** – Let commissioners choose anything from a light-hearted tease to a full-on savage burn before sending the recap.
2. 🧊 **Cooldown compliments** – Pair each harsh roast with a short, sincere compliment to keep league vibes friendly and balanced.
3. 🏆 **Badge cabinet** – Track outrageous wins, heartbreaking losses, and wild waiver moves with collectible trophies for every manager.
4. 📸 **Meme & GIF injector** – Auto-generate a meme or GIF that matches the narrative of the matchup’s roast or praise.
5. 📰 **Weekly smack-talk digest** – Bundle the best burns, praiseworthy feats, and standout stats into a shareable newsletter for the league.

## Product Decisions & Ops Playbook

Looking for deeper guidance on how to extend the app? Check out [`docs/experience-strategy.md`](docs/experience-strategy.md) for decisions around Sleeper automation, roast tone logic, formatting defaults, data storage, and error handling.

## Contributing

1. Fork the repo and create a feature branch.
2. Make your changes (no dependency installation required).
3. Submit a pull request describing your updates and testing notes.
