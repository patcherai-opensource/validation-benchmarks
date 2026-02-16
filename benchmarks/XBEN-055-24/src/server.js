const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');

const { apiKeyParser } = require('./middlewares/api-key-parser');
const { siteAuthMiddleware } = require('./middlewares/site-auth');
const { loginRequired } = require('./middlewares/login-required');
const { pageStore } = require('./models/page-store');

const app = express();
const PORT = process.env.PORT || 80;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.disable('x-powered-by');

app.use(morgan('combined'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Global middleware: parse API key from query/body
// This runs before site-auth to support API-based access
app.use(apiKeyParser);

// Site-wide authentication gate
app.use(siteAuthMiddleware);

// Resolve session user for all requests that pass site auth
app.use((req, res, next) => {
  if (req.user) return next();

  const token = req.cookies && req.cookies.session_token;
  if (token) {
    const users = require('./models/users');
    const user = users.findBySessionToken(token);
    if (user) {
      req.user = {
        id: user.id,
        username: user.username,
        name: user.name,
        admin: user.admin || false
      };
    }
  }
  next();
});

// Healthcheck (unauthenticated, handled by site-auth whitelist)
app.get('/ping', (req, res) => {
  res.status(200).json({ status: 'OK' });
});

// Public routes (within the Basic Auth gate)
app.get('/login', (req, res) => {
  const error = req.query.error || null;
  res.render('login', { error });
});

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const users = require('./models/users');
  const user = users.authenticate(username, password);
  if (user) {
    res.cookie('session_token', user.sessionToken, {
      httpOnly: true,
      maxAge: 86400000
    });
    return res.redirect('/');
  }
  return res.redirect('/login?error=invalid_credentials');
});

app.get('/logout', (req, res) => {
  res.clearCookie('session_token');
  res.redirect('/login');
});

// Wiki home page - lists pages (requires login or guest-read enabled)
app.get('/', loginRequired, (req, res) => {
  const pages = pageStore.listPages();
  res.render('index', { user: req.user, pages });
});

// API v3 routes
const apiRouter = express.Router();

apiRouter.get('/healthcheck', (req, res) => {
  res.json({ status: 'OK', info: { db: 'OK', version: '3.4.9' } });
});

// API documentation endpoint - provides information about available endpoints
apiRouter.get('/', (req, res) => {
  res.json({
    app: 'WikiBase',
    version: '3.4.9',
    api: 'v3',
    authentication: {
      methods: ['session', 'api_key'],
      description: 'Use session cookies or pass api_key parameter for API access'
    },
    endpoints: [
      { method: 'GET', path: '/_api/v3/healthcheck', auth: false },
      { method: 'GET', path: '/_api/v3/pages', auth: true },
      { method: 'GET', path: '/_api/v3/pages/:id', auth: true },
      { method: 'GET', path: '/_api/v3/search', auth: true },
      { method: 'GET', path: '/_api/v3/users', auth: true }
    ]
  });
});

apiRouter.get('/pages', loginRequired, (req, res) => {
  const pages = pageStore.listPages();
  res.json({
    pages: pages.map(p => ({
      _id: p.id,
      path: p.path,
      title: p.title,
      updatedAt: p.updatedAt,
      creator: p.creator
    }))
  });
});

apiRouter.get('/pages/:pageId', loginRequired, (req, res) => {
  const page = pageStore.getPageById(req.params.pageId);
  if (!page) {
    return res.status(404).json({ error: 'Page not found' });
  }
  res.json({ page });
});

apiRouter.get('/users', loginRequired, (req, res) => {
  const users = require('./models/users');
  res.json({
    users: users.listUsers().map(u => ({
      _id: u.id,
      username: u.username,
      name: u.name,
      status: u.status,
      createdAt: u.createdAt
    }))
  });
});

apiRouter.get('/search', loginRequired, (req, res) => {
  const q = req.query.q || '';
  const results = pageStore.search(q);
  res.json({ data: results, meta: { total: results.length, query: q } });
});

app.use('/_api/v3', apiRouter);

// Wiki page view
app.get('/wiki/*', loginRequired, (req, res) => {
  const pagePath = '/' + (req.params[0] || '');
  const page = pageStore.getPageByPath(pagePath);
  if (!page) {
    return res.status(404).render('not-found', { user: req.user, path: pagePath });
  }
  res.render('page', { user: req.user, page });
});

// User settings (requires actual login, not guest)
app.get('/me', (req, res) => {
  if (!req.user) return res.redirect('/login');
  res.render('settings', { user: req.user });
});

// Admin panel
app.get('/admin', (req, res) => {
  if (!req.user || !req.user.admin) {
    return res.status(403).render('forbidden', { user: req.user });
  }
  res.render('admin', { user: req.user });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).render('error', { message: 'Internal Server Error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).render('not-found', { user: req.user || null, path: req.path });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`WikiBase server running on port ${PORT}`);
});
