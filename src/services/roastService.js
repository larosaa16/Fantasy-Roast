import { loadEnv } from '../config/env.js';
import { logger } from '../utils/logger.js';

const env = loadEnv();

const buildPrompt = ({ matchup }) => {
  const [teamA, teamB] = matchup.teams;

  const formatTeam = (team, label) => {
    const starters = (team.players ?? []).filter((player) => player.started);
    const bench = (team.players ?? []).filter((player) => !player.started);
    const startersList = starters
      .map((player) =>
        `${player.playerName} (${player.points.toFixed(2)} pts${
          player.projectedPoints ? `, ${player.projectedPoints.toFixed(2)} proj` : ''
        })`
      )
      .join('\n');
    const benchList = bench
      .map((player) =>
        `${player.playerName} (${player.points.toFixed(2)} pts${
          player.projectedPoints ? `, ${player.projectedPoints.toFixed(2)} proj` : ''
        })`
      )
      .join('\n');

    return (
      `## ${label}: ${team.teamName} (${team.manager.displayName})\n` +
      `Total: ${team.points.toFixed(2)} pts${team.projectedPoints ? ` | Projected: ${team.projectedPoints.toFixed(2)}` : ''}\n` +
      `Starters:\n${startersList || 'No starters data'}\n` +
      `Bench:\n${benchList || 'No bench data'}`
    );
  };

  return (
    'You are a witty but light-hearted fantasy football roast master. Celebrate the winner and tease the loser without being mean spirited or offensive.' +
    `\n\nMatchup Week ${matchup.week} (${matchup.platform.toUpperCase()} - League ${matchup.leagueId})\n` +
    `${formatTeam(teamA, 'Team A')}\n\n${formatTeam(teamB, 'Team B')}\n\n` +
    'Provide a JSON response with two fields: "praise" complimenting the winning manager, and "roast" poking fun at the losing manager\'s decisions. Keep each under 75 words.'
  );
};

export const createRoast = async (request) => {
  const prompt = buildPrompt(request);
  const [teamA, teamB] = request.matchup.teams;
  const winner = teamA.points >= teamB.points ? teamA : teamB;
  const loser = winner === teamA ? teamB : teamA;

  const response = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4.1-mini',
      input: [
        {
          role: 'system',
          content: 'You are a JSON API that only returns valid JSON without additional commentary.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      response_format: {
        type: 'json_schema',
        json_schema: {
          name: 'roast_response',
          schema: {
            type: 'object',
            additionalProperties: false,
            required: ['praise', 'roast'],
            properties: {
              praise: { type: 'string' },
              roast: { type: 'string' }
            }
          }
        }
      }
    })
  });

  if (!response.ok) {
    const errorBody = await response.text();
    logger.error('OpenAI request failed', { status: response.status, body: errorBody });
    throw new Error('Failed to generate roast.');
  }

  const completion = await response.json();
  const outputText = completion.output?.[0]?.content?.[0]?.text;
  if (!outputText) {
    logger.error('OpenAI response missing text output', { completion });
    throw new Error('Failed to generate roast.');
  }

  let parsed;
  try {
    parsed = JSON.parse(outputText);
  } catch (error) {
    logger.error('Failed to parse OpenAI response', { outputText, error });
    throw new Error('Failed to parse roast.');
  }

  return {
    matchupId: request.matchup.id,
    week: request.matchup.week,
    leagueId: request.matchup.leagueId,
    platform: request.matchup.platform,
    winner,
    loser,
    praise: parsed.praise,
    roast: parsed.roast
  };
};
