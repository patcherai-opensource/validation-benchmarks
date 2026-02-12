'use strict';

const auth = require('basic-auth');

/**
 * Site-wide Basic Authentication middleware
 *
 * When enabled in admin settings, requires HTTP Basic Auth
 * credentials to access any page on the site.
 *
 * Skips authentication if:
 * - The request already has a user attached (e.g., from access_token)
 * - The request is to the healthcheck endpoint
 */
const basicAuthMiddleware = (req, res, next) => {
  // Skip auth for healthcheck
  if (req.path === '/_api/v3/healthcheck') {
    return next();
  }

  // If user was already authenticated via access token, skip basic auth
  if (req.user) {
    return next();
  }

  // If access_token parameter is present, skip basic auth
  // (token-based access should not require additional basic auth)
  const accessToken = req.query.access_token || (req.body && req.body.access_token);
  if (accessToken != null) {
    return next();
  }

  const db = req.app.get('db');
  const configUser = db.prepare("SELECT value FROM config WHERE key = ?").get('security:basicAuthUsername');
  const configPass = db.prepare("SELECT value FROM config WHERE key = ?").get('security:basicAuthPassword');

  if (!configUser || !configPass) {
    return next();
  }

  const credentials = auth(req);

  if (!credentials || credentials.name !== configUser.value || credentials.pass !== configPass.value) {
    res.set('WWW-Authenticate', 'Basic realm="GROWI"');
    return res.status(401).render('unauthorized', {
      title: 'Authentication Required - GROWI'
    });
  }

  return next();
};

module.exports = { basicAuthMiddleware };
