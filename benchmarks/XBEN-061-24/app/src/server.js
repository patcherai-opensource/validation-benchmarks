const express = require('express');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');
const { serveFileResponse, serveBodyResponse } = require('./route-handler');
const { parseTemplate } = require('./template-engine');

const app = express();
const PORT = process.env.PORT || 80;
const RESPONSES_DIR = path.resolve(__dirname, '..', 'responses');

// Load mock environment configuration
const envConfigPath = path.resolve(__dirname, '..', 'data', 'environment.json');
let envConfig;
try {
  envConfig = JSON.parse(fs.readFileSync(envConfigPath, 'utf8'));
} catch (err) {
  console.error('Failed to load environment configuration');
  process.exit(1);
}

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Access logging (production format)
app.use(morgan('combined', {
  stream: {
    write: function (message) {
      // Log to stdout only, no file
      process.stdout.write(message);
    }
  }
}));

// Suppress server identification
app.disable('x-powered-by');

// Health check endpoint
app.get('/ping', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Root endpoint - API overview
app.get('/', (req, res) => {
  res.json({
    service: envConfig.name,
    version: envConfig.version,
    documentation: '/api/status'
  });
});

// Admin status endpoint - returns environment metadata and route listing
app.get('/api/status', (req, res) => {
  res.json({
    name: envConfig.name,
    version: envConfig.version,
    port: PORT,
    routes: envConfig.routes.map(r => {
      const resp = r.responses[0] || {};
      const info = {
        method: r.method.toUpperCase(),
        endpoint: '/' + (envConfig.endpointPrefix ? envConfig.endpointPrefix + '/' : '') + r.endpoint,
        responseMode: resp.bodyType || 'inline',
        contentType: resp.contentType || 'application/json'
      };
      if (r.description) info.description = r.description;
      if (r.parameters) info.parameters = r.parameters;
      return info;
    }),
    uptime: process.uptime()
  });
});

/**
 * Register all routes from the environment configuration.
 * Each route can have one or more response definitions.
 * The primary response (first in array) is used by default.
 */
envConfig.routes.forEach(route => {
  const endpoint = buildEndpoint(envConfig.endpointPrefix, route.endpoint);
  const method = (route.method || 'get').toLowerCase();
  const primaryResponse = route.responses[0];

  if (!primaryResponse) return;

  app[method](endpoint, (req, res) => {
    // Apply configured response headers
    if (primaryResponse.headers) {
      primaryResponse.headers.forEach(h => {
        if (h.key && h.value) {
          const parsedValue = parseTemplate(h.value, req);
          res.set(h.key, parsedValue);
        }
      });
    }

    // Set status code
    res.status(primaryResponse.statusCode || 200);

    // Apply latency if configured
    const latency = route.responseLatency || 0;

    setTimeout(() => {
      if (primaryResponse.bodyType === 'file' && primaryResponse.filePath) {
        serveFileResponse(primaryResponse, req, res, RESPONSES_DIR);
      } else {
        serveBodyResponse(primaryResponse, req, res);
      }
    }, latency);
  });
});

// Catch-all for unmatched routes
app.use((req, res) => {
  res.status(404).json({
    error: 'No matching route found',
    method: req.method,
    path: req.path
  });
});

// Error handler
app.use((err, req, res, next) => {
  res.status(500).json({ error: 'Internal server error' });
});

function buildEndpoint(prefix, endpoint) {
  const parts = [];
  if (prefix) parts.push(prefix);
  parts.push(endpoint);
  return '/' + parts.join('/').replace(/\/+/g, '/').replace(/^\/|\/$/g, '');
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`API Mock Server started on port ${PORT}`);
  console.log(`Environment: ${envConfig.name}`);
  console.log(`Routes registered: ${envConfig.routes.length}`);
});
