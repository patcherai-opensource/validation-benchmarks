'use strict';

/**
 * Access Token Parser middleware
 *
 * Parses access_token from query string or request body
 * and attaches the authenticated user to the request.
 *
 * This is used for API access with personal tokens.
 */
const accessTokenParser = (req, res, next) => {
  const accessToken = req.query.access_token || (req.body && req.body.access_token);

  if (accessToken == null || typeof accessToken !== 'string') {
    return next();
  }

  const db = req.app.get('db');

  try {
    const user = db.prepare('SELECT * FROM users WHERE apiToken = ?').get(accessToken);

    if (user == null) {
      return next();
    }

    // Attach user to request (without sensitive fields)
    req.user = {
      id: user.id,
      username: user.username,
      name: user.name,
      email: user.email,
      isAdmin: user.isAdmin,
      status: user.status
    };
  } catch (err) {
    // Log error but don't block the request
    console.error('Error in accessTokenParser:', err.message);
  }

  return next();
};

module.exports = { accessTokenParser };
