import { EspnConnector } from '../platforms/espn/connector.js';
import { SleeperConnector } from '../platforms/sleeper/connector.js';
import { YahooConnector } from '../platforms/yahoo/connector.js';

const connectors = {
  sleeper: new SleeperConnector(),
  yahoo: new YahooConnector(),
  espn: new EspnConnector()
};

export const getMatchupsForWeek = async ({ platform, leagueId, week }) => {
  const connector = connectors[platform];
  if (!connector) {
    throw new Error(`Unsupported platform: ${platform}`);
  }

  return connector.getWeeklyMatchups({ leagueId, week });
};
