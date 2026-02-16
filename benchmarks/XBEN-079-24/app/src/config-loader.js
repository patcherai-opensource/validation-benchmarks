const fs = require('fs');
const path = require('path');

/**
 * Load and validate the mock environment configuration file.
 * The environment file defines routes, responses, and behavior
 * for the mock API server.
 */
function loadEnvironmentConfig(configPath) {
  if (!fs.existsSync(configPath)) {
    console.error(`Environment config not found: ${configPath}`);
    process.exit(1);
  }

  try {
    const raw = fs.readFileSync(configPath, 'utf-8');
    const config = JSON.parse(raw);

    // Validate required fields
    if (!config.name || !config.routes) {
      throw new Error('Invalid environment config: missing name or routes');
    }

    // Set defaults
    config.port = config.port || 80;
    config.endpointPrefix = config.endpointPrefix || '';
    config.cors = config.cors !== false;
    config.version = config.version || '2.4.1';
    config.dataDir = path.dirname(configPath);

    return config;
  } catch (err) {
    console.error(`Failed to parse environment config: ${err.message}`);
    process.exit(1);
  }
}

module.exports = { loadEnvironmentConfig };
