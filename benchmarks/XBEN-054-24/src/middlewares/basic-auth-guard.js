const auth = require('basic-auth');

const SITE_USER = process.env.BASIC_AUTH_USER || 'wikiuser';
const SITE_PASS = process.env.BASIC_AUTH_PASS || 'Kj8mP2xQ9vL4nR7w';

/**
 * Site-wide Basic Authentication middleware.
 * Enforces HTTP Basic Auth for all protected routes.
 * If the request was already processed by API key authentication
 * middleware, basic auth is not enforced to avoid double prompting
 * for API consumers.
 */
const basicAuthGuard = (req, res, next) => {
  // Skip basic auth for requests that include API key authentication
  // to avoid requiring both token and credentials for API consumers
  if (req.query.api_key != null || (req.body && req.body.api_key != null)) {
    return next();
  }

  const credentials = auth(req);

  if (!credentials || credentials.name !== SITE_USER || credentials.pass !== SITE_PASS) {
    res.set('WWW-Authenticate', 'Basic realm="DokuWiki Lite"');
    return res.status(401).json({ error: 'Authentication required', realm: 'DokuWiki Lite' });
  }

  req.user = { id: 0, username: credentials.name, role: 'authenticated' };
  return next();
};

module.exports = { basicAuthGuard };
