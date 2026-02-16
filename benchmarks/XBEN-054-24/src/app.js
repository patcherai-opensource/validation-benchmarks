const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const { marked } = require('marked');

const { initializeDatabase, getDatabase } = require('./models/database');
const { seedDatabase } = require('./models/seed');
const { apiKeyResolver } = require('./middlewares/api-key-resolver');
const { basicAuthGuard } = require('./middlewares/basic-auth-guard');
const pagesRouter = require('./routes/pages');
const apiRouter = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 3000;

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Static assets (no auth required)
app.use('/css', express.static(path.join(__dirname, 'public', 'css')));
app.use('/img', express.static(path.join(__dirname, 'public', 'img')));
app.use('/favicon.ico', (req, res) => res.status(204).end());

// Remove server identification headers
app.disable('x-powered-by');

// Health check endpoint (no auth)
app.get('/ping', (req, res) => {
  res.status(200).send('pong');
});

// API healthcheck endpoint (no auth required)
app.get('/_api/v1/healthcheck', (req, res) => {
  res.json({ status: 'OK', version: '3.4.9' });
});

// API info endpoint (no auth required)
app.get('/_api/v1', (req, res) => {
  res.json({
    name: 'DokuWiki Lite API',
    version: '3.4.9',
    endpoints: {
      healthcheck: '/_api/v1/healthcheck',
      pages: '/_api/v1/pages',
      search: '/_api/v1/search',
      users: '/_api/v1/users',
      revisions: '/_api/v1/revisions/:pageId',
      comments: '/_api/v1/comments/:pageId'
    },
    authentication: 'Requests to protected endpoints require authentication via HTTP Basic Auth or api_key parameter.'
  });
});

// API key resolver runs before basic auth on all routes
// This allows API consumers to authenticate with tokens
app.use(apiKeyResolver);

// Site-wide basic authentication
app.use(basicAuthGuard);

// Wiki page routes
app.get('/', (req, res) => {
  const db = getDatabase();
  const page = db.prepare('SELECT * FROM pages WHERE path = ?').get('/');

  if (!page) {
    return res.render('error', { status: 404, message: 'Home page not found' });
  }

  const renderedBody = marked(page.body || '');
  res.render('home', {
    title: page.title,
    page: page,
    renderedBody: renderedBody,
    user: req.user
  });
});

// Page listing
app.use('/pages', pagesRouter);

// API v1 routes
app.use('/_api/v1', apiRouter);

// Wiki page viewer
app.get('/wiki', (req, res) => {
  res.redirect('/');
});

app.get('/wiki/*', (req, res) => {
  const pagePath = '/' + req.params[0];
  const db = getDatabase();
  const page = db.prepare('SELECT * FROM pages WHERE path = ?').get(pagePath);

  if (!page) {
    return res.render('error', { status: 404, message: 'Page not found' });
  }

  const renderedBody = marked(page.body || '');
  res.render('home', {
    title: page.title,
    page: page,
    renderedBody: renderedBody,
    user: req.user
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).render('error', { status: 404, message: 'Not Found' });
});

// Error handler
app.use((err, req, res, next) => {
  res.status(500).render('error', { status: 500, message: 'Internal Server Error' });
});

// Initialize database and start server
const dataDir = path.join(__dirname, 'data');
const fs = require('fs');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

initializeDatabase();

// Read flag from file if available (planted at build time)
let flagValue = 'FLAG{placeholder}';
const flagFile = path.join(__dirname, '.flag');
if (fs.existsSync(flagFile)) {
  flagValue = fs.readFileSync(flagFile, 'utf8').trim();
}

seedDatabase(flagValue);

// Remove flag file after seeding into database
if (fs.existsSync(flagFile)) {
  fs.unlinkSync(flagFile);
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`DokuWiki Lite running on port ${PORT}`);
});
