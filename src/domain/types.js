/**
 * @typedef {('sleeper'|'yahoo'|'espn')} Platform
 */

/**
 * @typedef {{
 *  id: string;
 *  displayName: string;
 * }} Manager
 */

/**
 * @typedef {{
 *  playerId: string;
 *  playerName: string;
 *  points: number;
 *  projectedPoints?: number;
 *  position?: string;
 *  team?: string;
 *  started: boolean;
 * }} PlayerPerformance
 */

/**
 * @typedef {{
 *  teamId: string;
 *  teamName: string;
 *  manager: Manager;
 *  points: number;
 *  projectedPoints?: number;
 *  players: PlayerPerformance[];
 * }} TeamMatchup
 */

/**
 * @typedef {{
 *  id: string;
 *  week: number;
 *  platform: Platform;
 *  leagueId: string;
 *  teams: [TeamMatchup, TeamMatchup];
 * }} Matchup
 */

/**
 * @typedef {{ matchup: Matchup }} RoastRequest
 */

/**
 * @typedef {{
 *  matchupId: string;
 *  week: number;
 *  leagueId: string;
 *  platform: Platform;
 *  winner: TeamMatchup;
 *  loser: TeamMatchup;
 *  roast: string;
 *  praise: string;
 * }} RoastResult
 */

export {};
