'use strict';

const express = require('express');
const path = require('path');
const fs = require('fs');
const morgan = require('morgan');
const { sendFile, sendFileWithCallback, sendJsonBody, templateParser } = require('./libs/route-handler');

const app = express();
const PORT = process.env.PORT || 80;
const DATA_DIR = path.resolve(__dirname, '..', 'data');
const ENVIRONMENTS_DIR = path.resolve(DATA_DIR, 'environments');

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined', {
  stream: fs.createWriteStream('/dev/null')
}));

// Disable headers that leak info
app.disable('x-powered-by');

/**
 * Load environment configuration from JSON files.
 * Each environment defines routes, their responses, and behavior.
 */
function loadEnvironments() {
  const environments = [];
  if (!fs.existsSync(ENVIRONMENTS_DIR)) {
    return environments;
  }
  const files = fs.readdirSync(ENVIRONMENTS_DIR).filter(f => f.endsWith('.json'));
  for (const file of files) {
    try {
      const data = JSON.parse(fs.readFileSync(path.join(ENVIRONMENTS_DIR, file), 'utf8'));
      environments.push(data);
    } catch (e) {
      console.error(`Failed to load environment ${file}:`, e.message);
    }
  }
  return environments;
}

/**
 * Register routes from environment configurations.
 */
function registerEnvironmentRoutes(environment) {
  if (!environment.routes) return;

  for (const route of environment.routes) {
    const method = (route.method || 'GET').toLowerCase();
    const routePath = route.endpoint;

    if (!routePath) continue;

    app[method](routePath, (req, res) => {
      const response = route.responses && route.responses[0];
      if (!response) {
        res.status(200).json({ message: 'OK' });
        return;
      }

      // Add latency if configured
      const latency = response.latency || 0;

      setTimeout(() => {
        // Set custom headers if configured
        if (response.headers) {
          for (const header of response.headers) {
            const value = templateParser.parse(header.value, req);
            res.set(header.key, value);
          }
        }

        // Handle different response types
        if (response.filePath) {
          // File response - serve a file from the data directory
          sendFile(res, response.filePath, req, DATA_DIR);
        } else if (response.body) {
          // Body response - return template-processed JSON body
          sendJsonBody(res, response.body, req, response.statusCode);
        } else {
          res.status(response.statusCode || 200).json({ status: 'ok' });
        }
      }, latency);
    });
  }
}

// ============================================================
// Built-in management and health endpoints
// ============================================================

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', uptime: process.uptime() });
});

// Root - Dashboard UI
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'dashboard.html'));
});

// API info endpoint
app.get('/api/info', (req, res) => {
  const environments = loadEnvironments();
  res.json({
    name: 'Mockoon Server',
    version: '9.1.0',
    environments: environments.length,
    status: 'running'
  });
});

// List configured environments
app.get('/api/environments', (req, res) => {
  const environments = loadEnvironments();
  const summary = environments.map(env => ({
    name: env.name,
    port: env.port,
    routeCount: env.routes ? env.routes.length : 0,
    enabled: env.enabled !== false
  }));
  res.json(summary);
});

// List all routes across environments
app.get('/api/routes', (req, res) => {
  const environments = loadEnvironments();
  const routes = [];
  for (const env of environments) {
    if (env.enabled === false || !env.routes) continue;
    for (const route of env.routes) {
      const response = route.responses && route.responses[0];
      routes.push({
        method: (route.method || 'GET').toUpperCase(),
        endpoint: route.endpoint,
        responseType: response && response.filePath ? 'file' : 'json',
        statusCode: response ? (response.statusCode || 200) : 200,
        environment: env.name
      });
    }
  }
  res.json(routes);
});

// ============================================================
// Load and register all environment routes
// ============================================================
const environments = loadEnvironments();
for (const env of environments) {
  if (env.enabled !== false) {
    registerEnvironmentRoutes(env);
  }
}

console.log(`Loaded ${environments.length} environment(s)`);

// ============================================================
// 404 handler
// ============================================================
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    status: 404,
    path: req.path
  });
});

// ============================================================
// Start the server
// ============================================================
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Mockoon server running on port ${PORT}`);
});
