const defaultPlayer = (playerId, playersPoints, starters) => ({
  playerId,
  playerName: playerId,
  points: playersPoints[playerId] ?? 0,
  started: starters.includes(playerId)
});

const toTeamMatchup = ({ roster, matchup, users }) => {
  const manager = users.find((user) => user.user_id === roster.owner_id);

  return {
    teamId: String(roster.roster_id),
    teamName: roster.display_name,
    manager: {
      id: manager?.user_id ?? roster.owner_id,
      displayName: manager?.display_name ?? roster.display_name
    },
    points: matchup.points,
    players: (roster.players ?? []).map((playerId) =>
      defaultPlayer(playerId, matchup.players_points ?? {}, matchup.starters ?? [])
    )
  };
};

export const mapSleeperMatchup = ({ matchups, rosters, users, leagueId, week }) => {
  const matchupsById = new Map();
  (matchups ?? []).forEach((matchup) => {
    const list = matchupsById.get(matchup.matchup_id) ?? [];
    list.push(matchup);
    matchupsById.set(matchup.matchup_id, list);
  });

  const rostersById = new Map();
  (rosters ?? []).forEach((roster) => rostersById.set(roster.roster_id, roster));

  return Array.from(matchupsById.entries())
    .filter(([, teams]) => teams.length === 2)
    .map(([matchupId, teams]) => {
      const [home, away] = teams;
      const homeRoster = rostersById.get(home.roster_id);
      const awayRoster = rostersById.get(away.roster_id);
      if (!homeRoster || !awayRoster) {
        throw new Error(`Missing roster data for matchup ${matchupId}`);
      }

      const homeTeam = toTeamMatchup({ roster: homeRoster, matchup: home, users: users ?? [] });
      const awayTeam = toTeamMatchup({ roster: awayRoster, matchup: away, users: users ?? [] });

      return {
        id: `${leagueId}-${week}-${matchupId}`,
        week,
        leagueId,
        platform: 'sleeper',
        teams: [homeTeam, awayTeam]
      };
    });
};
