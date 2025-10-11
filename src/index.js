import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEnv } from './config/env.js';
import { handleApiRequest } from './http/router.js';
import { logger } from './utils/logger.js';

const env = loadEnv();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.resolve(__dirname, '../public');

const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon'
};

const MAX_BODY_SIZE_BYTES = 1_048_576; // 1 MiB

const readBody = (req) =>
  new Promise((resolve, reject) => {
    let raw = '';
    let bytes = 0;
    let rejected = false;

    req.on('data', (chunk) => {
      if (rejected) {
        return;
      }

      bytes += chunk.length;
      if (bytes > MAX_BODY_SIZE_BYTES) {
        rejected = true;
        const error = new Error('Payload too large');
        error.code = 'PAYLOAD_TOO_LARGE';
        reject(error);
        return;
      }

      raw += chunk;
    });
    req.on('end', () => {
      if (rejected) {
        return;
      }

      resolve(raw);
    });
    req.on('error', (error) => {
      if (rejected) {
        return;
      }

      reject(error);
    });
  });

const serveStatic = async (req, res, url) => {
  const requestPath = url.pathname === '/' ? '/index.html' : url.pathname;
  const filePath = path.join(publicDir, requestPath);

  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  try {
    const fileStat = await stat(filePath);
    if (!fileStat.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }

    const ext = path.extname(filePath);
    const contentType = contentTypes[ext] ?? 'application/octet-stream';
    const content = await readFile(filePath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  } catch (error) {
    if (error.code === 'ENOENT') {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }

    logger.error('Failed to serve static asset', { error: error.message });
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Internal Server Error');
  }
};

const server = http.createServer(async (req, res) => {
  if (!req.url || !req.method) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Invalid request' }));
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);

  if (url.pathname.startsWith('/api')) {
    let parsedBody = null;

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      try {
        const rawBody = await readBody(req);
        if (rawBody) {
          parsedBody = JSON.parse(rawBody);
        }
      } catch (error) {
        if (error?.code === 'PAYLOAD_TOO_LARGE') {
          res.writeHead(413, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Payload too large' }));
          return;
        }

        logger.warn('Failed to parse request body as JSON', { error: error.message });
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON body' }));
        return;
      }
    }

    try {
      const result = await handleApiRequest({ method: req.method, url, body: parsedBody });
      res.writeHead(result.statusCode, { 'Content-Type': 'application/json', ...(result.headers ?? {}) });
      res.end(JSON.stringify(result.body));
    } catch (error) {
      logger.error('Unhandled API error', { error: error.message });
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Internal Server Error' }));
    }

    return;
  }

  await serveStatic(req, res, url);
});

server.listen(env.PORT, () => {
  logger.info(`Fantasy Roast API listening on port ${env.PORT}`);
});
