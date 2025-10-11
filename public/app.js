const baseUrl = window.location.origin;

const matchupForm = document.getElementById('matchup-form');
const matchupResults = document.getElementById('matchup-results');
const roastForm = document.getElementById('roast-form');
const roastOutput = document.getElementById('roast-output');
const payloadField = document.getElementById('matchup-payload');

matchupForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  matchupResults.innerHTML = '<p>Loading matchups…</p>';

  const formData = new FormData(matchupForm);
  const platform = formData.get('platform')?.toString().trim();
  const leagueId = formData.get('leagueId')?.toString().trim();
  const week = formData.get('week')?.toString().trim();

  if (!platform || !leagueId || !week) {
    matchupResults.innerHTML = '<p class="error">All fields are required.</p>';
    return;
  }

  try {
    const response = await fetch(
      `${baseUrl}/api/leagues/${platform}/${leagueId}/matchups?week=${week}`
    );

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const payload = await response.json();
    const matchups = Array.isArray(payload) ? payload : payload?.matchups;
    if (!Array.isArray(matchups) || matchups.length === 0) {
      matchupResults.innerHTML =
        '<p>No matchups found. Double-check your league ID and week.</p>';
      return;
    }

    const template = document.getElementById('matchup-template');
    if (!(template instanceof HTMLTemplateElement)) {
      matchupResults.innerHTML = '<p class="error">Template missing from the page.</p>';
      return;
    }
    matchupResults.innerHTML = '';

    const templateRoot = template.content.firstElementChild;
    if (!templateRoot) {
      matchupResults.innerHTML = '<p class="error">Template content missing.</p>';
      return;
    }

    matchups.forEach((matchup) => {
      const clonedNode = templateRoot.cloneNode(true);
      if (!(clonedNode instanceof HTMLElement)) {
        return;
      }

      const node = clonedNode;
      const title = node.querySelector('.matchup__title');
      const meta = node.querySelector('.matchup__meta');
      const teams = node.querySelector('.matchup__teams');
      const copyButton = node.querySelector('.matchup__copy');

      if (!(title instanceof HTMLElement) || !(meta instanceof HTMLElement) || !(teams instanceof HTMLElement)) {
        return;
      }

      if (!(copyButton instanceof HTMLButtonElement)) {
        return;
      }

      title.textContent = `${matchup.matchupId ?? matchup.id ?? 'Matchup'} · Week ${
        matchup.week ?? week
      }`;
      meta.textContent = `${matchup.teams?.length ?? 0} teams · ${matchup.platform ?? platform}`;

      teams.innerHTML = '';
      const matchupTeams = Array.isArray(matchup.teams) ? matchup.teams : [];
      const highScore = matchupTeams.reduce((max, current) => {
        const currentPoints = typeof current.points === 'number' ? current.points : max;
        return currentPoints > max ? currentPoints : max;
      }, -Infinity);

      matchupTeams.forEach((team) => {
        const teamNode = document.createElement('div');
        teamNode.className = 'team';

        const points = typeof team.points === 'number' ? team.points : undefined;
        const isWinner = team.outcome === 'win' || (points !== undefined && points === highScore);
        const isLoser = team.outcome === 'loss';

        if (isWinner) teamNode.classList.add('team--winner');
        if (isLoser) teamNode.classList.add('team--loser');

        const name = document.createElement('div');
        name.className = 'team__name';

        const teamTitle = document.createElement('strong');
        teamTitle.textContent = team.teamName ?? 'Team';

        const managerName = document.createElement('span');
        managerName.textContent = team.manager?.displayName ?? 'Manager TBD';

        name.append(teamTitle, managerName);

        const score = document.createElement('span');
        score.className = 'team__score';
        const pointsLabel =
          typeof points === 'number'
            ? `${points.toFixed(2)} pts`
            : team.points
            ? `${team.points} pts`
            : '—';
        score.textContent = pointsLabel;

        teamNode.append(name, score);
        teams.append(teamNode);
      });

      copyButton.addEventListener('click', () => {
        if (payloadField instanceof HTMLTextAreaElement) {
          payloadField.value = JSON.stringify(matchup, null, 2);
          payloadField.focus();
        }

        const roastLeague = document.getElementById('roast-league');
        if (roastLeague instanceof HTMLInputElement) {
          roastLeague.value = leagueId;
        }

        const roastPlatform = document.getElementById('roast-platform');
        if (roastPlatform instanceof HTMLSelectElement) {
          roastPlatform.value = platform;
        }

        const roastMatchup = document.getElementById('matchup-id');
        if (roastMatchup instanceof HTMLInputElement) {
          roastMatchup.value = matchup.matchupId ?? matchup.id ?? '';
        }
      });

      matchupResults.appendChild(node);
    });
  } catch (error) {
    console.error(error);
    matchupResults.innerHTML =
      '<p class="error">Could not load matchups right now. Check the console for details.</p>';
  }
});

roastForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  roastOutput.innerHTML = '<p>Summoning the roast…</p>';

  const formData = new FormData(roastForm);
  const platform = formData.get('platform')?.toString().trim();
  const leagueId = formData.get('leagueId')?.toString().trim();
  const matchupId = formData.get('matchupId')?.toString().trim();
  const payloadText = formData.get('payload')?.toString();

  if (!platform || !leagueId || !matchupId || !payloadText) {
    roastOutput.innerHTML = '<p class="error">All fields are required.</p>';
    return;
  }

  let payload;
  try {
    payload = JSON.parse(payloadText);
  } catch (error) {
    roastOutput.innerHTML = '<p class="error">Matchup payload must be valid JSON.</p>';
    return;
  }

  try {
    const response = await fetch(`${baseUrl}/api/leagues/${platform}/${leagueId}/roast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ matchup: payload })
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed with status ${response.status}`);
    }

    const roastPayload = await response.json();
    const result = roastPayload?.roast ?? roastPayload;

    roastOutput.innerHTML = '';

    const article = document.createElement('article');
    article.className = 'matchup';

    const header = document.createElement('header');
    header.className = 'matchup__header';

    const winnerHeading = document.createElement('h3');
    winnerHeading.className = 'matchup__title';
    winnerHeading.textContent = `Winner: ${
      result.winner?.manager?.displayName ?? result.winner?.teamName ?? 'TBD'
    }`;

    const loserMeta = document.createElement('span');
    loserMeta.className = 'matchup__meta';
    loserMeta.textContent = `Loser: ${
      result.loser?.manager?.displayName ?? result.loser?.teamName ?? 'TBD'
    }`;

    header.append(winnerHeading, loserMeta);

    const teamsContainer = document.createElement('div');
    teamsContainer.className = 'matchup__teams';

    const praiseCard = document.createElement('div');
    praiseCard.className = 'team team--winner';
    const praiseBody = document.createElement('div');
    praiseBody.className = 'team__name';
    const praiseTitle = document.createElement('strong');
    praiseTitle.textContent = 'Praise';
    const praiseCopy = document.createElement('span');
    praiseCopy.textContent = result.praise ?? 'No praise generated.';
    praiseBody.append(praiseTitle, praiseCopy);
    praiseCard.append(praiseBody);

    const roastCard = document.createElement('div');
    roastCard.className = 'team team--loser';
    const roastBody = document.createElement('div');
    roastBody.className = 'team__name';
    const roastTitle = document.createElement('strong');
    roastTitle.textContent = 'Roast';
    const roastCopy = document.createElement('span');
    roastCopy.textContent = result.roast ?? 'No roast generated.';
    roastBody.append(roastTitle, roastCopy);
    roastCard.append(roastBody);

    teamsContainer.append(praiseCard, roastCard);

    article.append(header, teamsContainer);
    roastOutput.append(article);
  } catch (error) {
    console.error(error);
    roastOutput.innerHTML =
      '<p class="error">Unable to cook the roast. Verify your API keys and server logs.</p>';
  }
});

// Default payload to help onboarding
if (payloadField instanceof HTMLTextAreaElement && !payloadField.value) {
  payloadField.value = JSON.stringify(
    {
      id: 'demo-1',
      week: 1,
      leagueId: 'demo-league',
      platform: 'sleeper',
      teams: [
        {
          teamId: '111',
          teamName: 'Gridiron Gurus',
          manager: { id: 'alex', displayName: 'Alex' },
          points: 134.6,
          outcome: 'win'
        },
        {
          teamId: '222',
          teamName: 'Bye Week Bandits',
          manager: { id: 'jordan', displayName: 'Jordan' },
          points: 97.3,
          outcome: 'loss'
        }
      ]
    },
    null,
    2
  );
}
