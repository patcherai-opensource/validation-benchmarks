/**
 * Site-wide HTTP Basic Authentication middleware.
 * Protects all resources except whitelisted paths.
 * When enabled, all visitors must provide valid Basic Auth credentials
 * before accessing any page or API endpoint.
 */
const basicAuth = require('basic-auth');
const crypto = require('crypto');

// Site-wide auth credentials (set during deployment)
const SITE_USER = process.env.SITE_AUTH_USER || 'wikiadmin';
const SITE_PASS = process.env.SITE_AUTH_PASS || crypto.randomBytes(24).toString('hex');

// Paths exempt from site-wide basic auth
const PUBLIC_PATHS = ['/ping', '/_api/v3/healthcheck', '/_api/v3'];

const siteAuthMiddleware = (req, res, next) => {
  // Skip auth for health checks and public API endpoints
  const normalizedPath = req.path.replace(/\/+$/, '') || '/';
  if (PUBLIC_PATHS.includes(normalizedPath)) {
    return next();
  }

  // If the request includes an API key, defer to the API key
  // authentication flow rather than prompting for Basic Auth.
  // This allows API consumers to access resources without
  // needing to also provide Basic Auth credentials.
  if (req.apiKeyProvided) {
    return next();
  }

  // Enforce HTTP Basic Authentication
  const credentials = basicAuth(req);
  if (!credentials || credentials.name !== SITE_USER || credentials.pass !== SITE_PASS) {
    res.set('WWW-Authenticate', 'Basic realm="WikiBase"');
    return res.status(401).send('Authentication required');
  }

  return next();
};

module.exports = { siteAuthMiddleware };
