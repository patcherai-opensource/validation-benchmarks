'use strict';

/**
 * Login Required middleware
 *
 * Ensures the request has an authenticated user.
 * Used for admin routes and other protected resources.
 */
const loginRequired = (req, res, next) => {
  if (req.user && req.user.id) {
    return next();
  }

  res.status(403).render('forbidden', {
    title: 'Access Denied - GROWI'
  });
};

module.exports = { loginRequired };
