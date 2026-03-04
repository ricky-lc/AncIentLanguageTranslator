const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const handler = require('../api/translate');

const indexHtml = fs.readFileSync(path.resolve(__dirname, '..', 'index.html'));
const MAX_REQUEST_SIZE = 1_000_000;

const server = http.createServer((req, res) => {
  if (req.url === '/' && req.method === 'GET') {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.end(indexHtml);
    return;
  }

  if (req.url === '/api/translate') {
    let raw = '';
    req.on('data', (chunk) => {
      raw += chunk;
      if (raw.length > MAX_REQUEST_SIZE) {
        req.destroy();
      }
    });
    req.on('end', () => {
      req.body = raw;
      handler(req, res);
    });
    return;
  }

  res.statusCode = 404;
  res.end('Not found');
});

const port = process.env.PORT || 3000;
server.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Translator running at http://localhost:${port}`);
});
