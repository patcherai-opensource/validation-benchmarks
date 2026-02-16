/**
 * Middleware that ensures a user is authenticated before proceeding.
 * Returns 401 if no user is present on the request.
 */
const loginRequired = (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  return next();
};

/**
 * Middleware that requires admin role.
 */
const adminRequired = (req, res, next) => {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  return next();
};

module.exports = { loginRequired, adminRequired };
