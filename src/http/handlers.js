import { getMatchupsForWeek } from '../services/leagueService.js';
import { createRoast } from '../services/roastService.js';
import { storeRoast } from '../services/supabaseService.js';
import { logger } from '../utils/logger.js';

export const healthHandler = async () => ({
  statusCode: 200,
  body: { status: 'ok' }
});

export const getMatchupsHandler = async ({ params, query }) => {
  const { platform, leagueId } = params;
  const weekValue = query.get('week');
  const week = Number(weekValue ?? 1);

  if (!Number.isFinite(week) || week <= 0) {
    return {
      statusCode: 400,
      body: { error: 'week must be a positive number' }
    };
  }

  const matchups = await getMatchupsForWeek({ platform, leagueId, week });
  return { statusCode: 200, body: { matchups } };
};

export const roastMatchupHandler = async ({ params, body }) => {
  const { platform, leagueId } = params;
  const { matchup } = body ?? {};
  if (!matchup) {
    return {
      statusCode: 400,
      body: { error: 'matchup payload is required' }
    };
  }

  if (matchup.platform !== platform || matchup.leagueId !== leagueId) {
    return {
      statusCode: 400,
      body: { error: 'matchup platform/league mismatch' }
    };
  }

  const roast = await createRoast({ matchup });

  try {
    await storeRoast(roast);
  } catch (error) {
    logger.error('Failed to persist roast to Supabase', { error: error.message });
  }

  return { statusCode: 200, body: { roast } };
};
