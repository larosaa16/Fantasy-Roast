export class EspnConnector {
  async getWeeklyMatchups({ leagueId, week }) {
    console.warn('ESPN API integration not yet implemented. Returning empty matchup list.');

    return [
      {
        id: `${leagueId}-${week}-placeholder-espn`,
        leagueId,
        week,
        platform: 'espn',
        teams: [
          {
            teamId: '1',
            teamName: 'Placeholder Home',
            manager: { id: 'manager-home', displayName: 'Manager Home' },
            points: 0,
            players: []
          },
          {
            teamId: '2',
            teamName: 'Placeholder Away',
            manager: { id: 'manager-away', displayName: 'Manager Away' },
            points: 0,
            players: []
          }
        ]
      }
    ];
  }
}
