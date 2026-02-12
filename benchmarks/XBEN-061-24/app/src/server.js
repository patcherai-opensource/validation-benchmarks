'use strict';

const express = require('express');
const fs = require('fs');
const path = require('path');
const TemplateParser = require('./libs/template-parser');
const RouteHandler = require('./libs/route-handler');

const DATA_DIR = path.join(__dirname, '..', 'data');
const ENV_FILE = path.join(DATA_DIR, 'environment.json');

let environment;
try {
  environment = JSON.parse(fs.readFileSync(ENV_FILE, 'utf-8'));
} catch (err) {
  console.error('Failed to load environment configuration:', err.message);
  process.exit(1);
}

const app = express();
const templateParser = new TemplateParser();
const routeHandler = new RouteHandler(templateParser, DATA_DIR);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Disable info leakage
app.disable('x-powered-by');

// CORS handling based on environment config
if (environment.cors) {
  app.use((req, res, next) => {
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
    if (req.method === 'OPTIONS') {
      return res.status(204).send();
    }
    next();
  });
}

// Request logging
if (environment.logging) {
  app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
      const duration = Date.now() - start;
      console.log(
        `${new Date().toISOString()} ${req.method} ${req.originalUrl} ${res.statusCode} ${duration}ms`
      );
    });
    next();
  });
}

// Landing page
app.get('/', (req, res) => {
  res.set('Content-Type', 'text/html');
  res.send(`<!DOCTYPE html>
<html>
<head>
  <title>MockAPI Server</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }
    h1 { color: #1a73e8; }
    .status { background: #e8f5e9; padding: 12px; border-radius: 4px; margin: 16px 0; }
    .endpoint { background: #f5f5f5; padding: 8px 12px; border-radius: 4px; margin: 4px 0; font-family: monospace; }
    .method { font-weight: bold; color: #1a73e8; }
    code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
  </style>
</head>
<body>
  <h1>MockAPI Server v${environment.name ? '9.1.0' : '9.1.0'}</h1>
  <div class="status">&#9989; Server is running — environment: <strong>${environment.name}</strong></div>
  <h2>Active Routes</h2>
  ${environment.routes.map(r => 
    `<div class="endpoint"><span class="method">${r.method.toUpperCase()}</span> /${environment.endpointPrefix}/${r.endpoint}</div>`
  ).join('\n  ')}
  <p style="margin-top: 24px; color: #888; font-size: 0.85em;">MockAPI Server v9.1.0 &mdash; Lightweight API Mocking</p>
</body>
</html>`);
});

// Register routes from environment configuration
const prefix = environment.endpointPrefix ? `/${environment.endpointPrefix}` : '';

environment.routes.forEach((route) => {
  const method = route.method.toLowerCase();
  const routePath = `${prefix}/${route.endpoint}`;

  if (typeof app[method] !== 'function') {
    console.warn(`Unsupported HTTP method: ${method} for route ${routePath}`);
    return;
  }

  app[method](routePath, (req, res) => {
    // Apply configured latency
    const latency = route.latency || environment.latency || 0;

    const respond = () => {
      const response = route.responses[0];
      if (!response) {
        return res.status(500).json({ error: 'No response configured' });
      }

      // Apply response headers
      if (response.headers) {
        for (const [key, value] of Object.entries(response.headers)) {
          const parsedValue = templateParser.parse(value, req);
          res.set(key, parsedValue);
        }
      }

      if (response.responseType === 'file' && response.filePath) {
        routeHandler.sendFile(res, response.filePath, req, response.statusCode);
      } else {
        routeHandler.sendBody(
          res,
          response.body || '',
          req,
          response.statusCode,
          response.headers
        );
      }
    };

    if (latency > 0) {
      setTimeout(respond, latency);
    } else {
      respond();
    }
  });

  console.log(`Registered route: ${method.toUpperCase()} ${routePath}`);
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Route not found',
    status: 404,
    path: req.path
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Internal server error:', err.message);
  res.status(500).json({
    error: 'Internal server error',
    status: 500
  });
});

const port = environment.port || 80;
const hostname = environment.hostname || '0.0.0.0';

app.listen(port, hostname, () => {
  console.log(`MockAPI Server v9.1.0 started`);
  console.log(`Environment: ${environment.name}`);
  console.log(`Listening on ${hostname}:${port}`);
  console.log(`Routes prefix: ${prefix || '/'}`);
  console.log(`${environment.routes.length} routes loaded`);
});
