const { getDatabase } = require('../models/database');

/**
 * Middleware to resolve API key from request parameters.
 * Intended for programmatic API access using user-issued tokens.
 * If a valid api_key is provided, attaches the corresponding user to the request.
 */
const apiKeyResolver = async (req, res, next) => {
  const apiKey = req.query.api_key || req.body.api_key;

  if (apiKey == null || typeof apiKey !== 'string') {
    return next();
  }

  const db = getDatabase();
  const user = db.prepare(
    'SELECT id, username, email, role, status FROM users WHERE api_token = ?'
  ).get(apiKey);

  if (user == null) {
    return next();
  }

  req.user = user;
  return next();
};

module.exports = { apiKeyResolver };
