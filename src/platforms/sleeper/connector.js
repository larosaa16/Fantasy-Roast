import { mapSleeperMatchup } from './mappers.js';

const fetchJson = async (url) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Sleeper API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
};

export class SleeperConnector {
  constructor() {
    this.baseUrl = 'https://api.sleeper.app/v1';
  }

  async getWeeklyMatchups({ leagueId, week }) {
    const [matchups, rosters, users] = await Promise.all([
      fetchJson(`${this.baseUrl}/league/${leagueId}/matchups/${week}`),
      fetchJson(`${this.baseUrl}/league/${leagueId}/rosters`),
      fetchJson(`${this.baseUrl}/league/${leagueId}/users`)
    ]);

    return mapSleeperMatchup({ matchups, rosters, users, leagueId, week });
  }
}
