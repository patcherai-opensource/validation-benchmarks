const express = require('express');
const path = require('path');
const fs = require('fs');
const cookieParser = require('cookie-parser');
const { loadEnvironmentConfig } = require('./config-loader');
const { createMockRoutes } = require('./route-handler');
const { createAdminRoutes } = require('./admin');

const app = express();
const PORT = process.env.PORT || 80;
const API_SECRET_PATH = '/etc/mockapi/api-secret.key';

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

app.disable('x-powered-by');

// Load mock environment configuration
const envConfig = loadEnvironmentConfig(
  path.join(__dirname, '..', 'data', 'environment.json')
);

// Validate API secret exists
if (fs.existsSync(API_SECRET_PATH)) {
  envConfig.apiSecretConfigured = true;
} else {
  envConfig.apiSecretConfigured = false;
}

// Serve the dashboard UI
app.use('/dashboard', express.static(path.join(__dirname, '..', 'views')));

// Admin API for managing the mock environment
createAdminRoutes(app, envConfig);

// Register all mock routes from the environment config
createMockRoutes(app, envConfig);

// Dashboard root redirect
app.get('/', (req, res) => {
  res.redirect('/dashboard');
});

app.listen(PORT, '0.0.0.0', () => {
  const ts = new Date().toISOString();
  console.log(`[${ts}] MockAPI Studio v${envConfig.version || '2.4.1'} started`);
  console.log(`[${ts}] Environment "${envConfig.name}" loaded with ${envConfig.routes.length} route(s)`);
  console.log(`[${ts}] Listening on port ${PORT}`);
});
