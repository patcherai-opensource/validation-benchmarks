'use strict';

const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');
const helmet = require('helmet');

const { initDatabase } = require('./models/database');
const { accessTokenParser } = require('./middlewares/access-token-parser');
const { basicAuthMiddleware } = require('./middlewares/basic-auth');
const { loginRequired } = require('./middlewares/login-required');
const pagesRouter = require('./routes/pages');
const apiRouter = require('./routes/api');
const adminRouter = require('./routes/admin');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize database
const db = initDatabase();
app.set('db', db);

// View engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Security headers
app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));

// Logging
app.use(morgan('combined', {
  skip: function (req) {
    return req.url === '/_api/v3/healthcheck';
  }
}));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Static files
app.use('/public', express.static(path.join(__dirname, 'public')));

// Health check endpoint (no auth required)
app.get('/_api/v3/healthcheck', (req, res) => {
  res.json({ status: 'OK', version: '3.4.9' });
});

// Access token parser runs before basic auth on all routes
// This middleware processes API tokens from query parameters
app.use(accessTokenParser);

// Site-wide basic authentication
// When enabled in admin settings, all pages require basic auth
const config = db.prepare('SELECT value FROM config WHERE key = ?').get('security:basicAuthEnabled');
if (config && config.value === 'true') {
  app.use(basicAuthMiddleware);
}

// API routes (token-based auth)
app.use('/_api', apiRouter);

// Admin routes
app.use('/_admin', loginRequired, adminRouter);

// Wiki page routes
app.use('/', pagesRouter);

// Error handler
app.use((err, req, res, next) => {
  res.status(err.status || 500);
  res.render('error', {
    title: 'Error - GROWI',
    message: 'An error occurred',
    status: err.status || 500
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`GROWI wiki server started on port ${PORT}`);
});

module.exports = app;
