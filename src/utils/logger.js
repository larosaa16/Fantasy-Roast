const format = (level, message, metadata) => {
  const timestamp = new Date().toISOString();
  const parts = [timestamp, level.toUpperCase(), message];
  if (metadata && Object.keys(metadata).length > 0) {
    parts.push(JSON.stringify(metadata));
  }
  return parts.join(' | ');
};

const log = (level, message, metadata) => {
  if (typeof message === 'object' && message !== null) {
    console.log(format(level, '', message));
    return;
  }

  console.log(format(level, String(message ?? ''), metadata));
};

export const logger = {
  debug(message, metadata) {
    if (process.env.LOG_LEVEL === 'debug') {
      log('debug', message, metadata);
    }
  },
  info(message, metadata) {
    log('info', message, metadata);
  },
  warn(message, metadata) {
    log('warn', message, metadata);
  },
  error(message, metadata) {
    log('error', message, metadata);
  }
};
