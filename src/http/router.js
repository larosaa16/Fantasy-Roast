import { getMatchupsHandler, healthHandler, roastMatchupHandler } from './handlers.js';

const notFound = {
  statusCode: 404,
  body: { error: 'Not found' }
};

const methodNotAllowed = {
  statusCode: 405,
  body: { error: 'Method not allowed' }
};

export const handleApiRequest = async ({ method, url, body }) => {
  const segments = url.pathname.split('/').filter(Boolean);

  if (segments.length === 1 && segments[0] === 'api') {
    if (method !== 'GET') {
      return methodNotAllowed;
    }

    return healthHandler();
  }

  if (segments.length === 2 && segments[0] === 'api' && segments[1] === 'health') {
    if (method !== 'GET') {
      return methodNotAllowed;
    }

    return healthHandler();
  }

  if (segments.length === 5 && segments[0] === 'api' && segments[1] === 'leagues') {
    const [, , platform, leagueId, resource] = segments;
    const params = { platform, leagueId };

    if (resource === 'matchups') {
      if (method !== 'GET') {
        return methodNotAllowed;
      }

      return getMatchupsHandler({ params, query: url.searchParams });
    }

    if (resource === 'roast') {
      if (method !== 'POST') {
        return methodNotAllowed;
      }

      return roastMatchupHandler({ params, body });
    }
  }

  return notFound;
};
