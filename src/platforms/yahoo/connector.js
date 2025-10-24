export class YahooConnector {
  async getWeeklyMatchups({ leagueId, week }) {
    console.warn('Yahoo API integration not yet implemented. Returning empty matchup list.');

    return [
      {
        id: `${leagueId}-${week}-placeholder-yahoo`,
        leagueId,
        week,
        platform: 'yahoo',
        teams: [
          {
            teamId: '1',
            teamName: 'Placeholder A',
            manager: { id: 'manager-a', displayName: 'Manager A' },
            points: 0,
            players: []
          },
          {
            teamId: '2',
            teamName: 'Placeholder B',
            manager: { id: 'manager-b', displayName: 'Manager B' },
            points: 0,
            players: []
          }
        ]
      }
    ];
  }
}
