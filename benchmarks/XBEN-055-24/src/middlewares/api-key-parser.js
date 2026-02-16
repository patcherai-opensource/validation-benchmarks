/**
 * Middleware to parse API key from request query or body.
 * Used for programmatic API access with user tokens.
 */
const users = require('../models/users');

const apiKeyParser = (req, res, next) => {
  const apiKey = req.query.api_key || req.body.api_key;
  if (apiKey == null || typeof apiKey !== 'string') {
    return next();
  }

  // Mark that API key authentication was attempted
  req.apiKeyProvided = true;

  const user = users.findByApiToken(apiKey);
  if (user == null) {
    return next();
  }

  req.user = {
    id: user.id,
    username: user.username,
    name: user.name,
    admin: user.admin || false
  };

  return next();
};

module.exports = { apiKeyParser };
