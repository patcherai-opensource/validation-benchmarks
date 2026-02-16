/**
 * Require login middleware.
 * Allows access if:
 * 1. User is authenticated (via session or API key), OR
 * 2. Guest reading is allowed (configurable)
 *
 * Guest reading is enabled by default to allow read-only access
 * to wiki content for users who have passed site-wide auth.
 */

const GUEST_READ_ALLOWED = process.env.GUEST_READ_ALLOWED !== 'false';

const loginRequired = (req, res, next) => {
  // Authenticated user
  if (req.user != null && typeof req.user === 'object' && req.user.id) {
    return next();
  }

  // Guest read access allowed
  if (GUEST_READ_ALLOWED) {
    return next();
  }

  // API routes return 403
  const baseUrl = req.baseUrl || '';
  if (baseUrl.match(/^\/_api\/.+$/)) {
    return res.status(403).json({ error: 'Login required' });
  }

  return res.redirect('/login');
};

module.exports = { loginRequired };
