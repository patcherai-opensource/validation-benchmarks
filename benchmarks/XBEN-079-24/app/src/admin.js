/**
 * Admin API endpoints for MockAPI Studio.
 * Provides read-only access to the environment configuration
 * and server status.
 */

function createAdminRoutes(app, envConfig) {
  // Health check
  app.get('/ping', (req, res) => {
    res.json({ status: 'ok' });
  });

  // Environment info
  app.get('/mockapi/status', (req, res) => {
    res.json({
      name: envConfig.name,
      version: envConfig.version,
      routeCount: envConfig.routes.length,
      cors: envConfig.cors,
      prefix: envConfig.endpointPrefix || '(none)',
      uptime: process.uptime(),
      dataDir: envConfig.dataDir,
      apiKeyAuth: envConfig.apiSecretConfigured
    });
  });

  // List configured routes (metadata only)
  app.get('/mockapi/routes', (req, res) => {
    const routes = envConfig.routes.map((r) => ({
      method: r.method || 'GET',
      endpoint: r.endpoint,
      responseCount: r.responses ? r.responses.length : 0,
      enabled: r.enabled !== false
    }));
    res.json({ routes });
  });
}

module.exports = { createAdminRoutes };
