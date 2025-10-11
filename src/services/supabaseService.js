import { loadEnv } from '../config/env.js';
import { logger } from '../utils/logger.js';

const env = loadEnv();

export const storeRoast = async (roast) => {
  const url = `${env.SUPABASE_URL}/rest/v1/roasts`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      apikey: env.SUPABASE_ANON_KEY,
      Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal'
    },
    body: JSON.stringify({
      matchup_id: roast.matchupId,
      week: roast.week,
      league_id: roast.leagueId,
      platform: roast.platform,
      winner_id: roast.winner.teamId,
      loser_id: roast.loser.teamId,
      praise: roast.praise,
      roast: roast.roast
    })
  });

  if (!response.ok) {
    const body = await response.text();
    logger.error('Failed to persist roast to Supabase', { status: response.status, body });
    throw new Error('Failed to store roast.');
  }
};
