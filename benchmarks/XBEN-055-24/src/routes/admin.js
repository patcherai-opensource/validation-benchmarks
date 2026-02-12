'use strict';

const express = require('express');
const router = express.Router();

// Admin dashboard
router.get('/', (req, res) => {
  const db = req.app.get('db');

  const pageCount = db.prepare('SELECT COUNT(*) as count FROM pages').get();
  const userCount = db.prepare('SELECT COUNT(*) as count FROM users').get();

  res.render('admin', {
    title: 'Admin - GROWI',
    user: req.user,
    stats: {
      pages: pageCount.count,
      users: userCount.count
    }
  });
});

// Admin settings
router.get('/settings', (req, res) => {
  const db = req.app.get('db');

  const configs = db.prepare('SELECT key, value FROM config').all();
  const configMap = {};
  configs.forEach(c => {
    if (!c.key.includes('Password') && !c.key.includes('password')) {
      configMap[c.key] = c.value;
    }
  });

  res.render('admin-settings', {
    title: 'Settings - GROWI',
    user: req.user,
    config: configMap
  });
});

module.exports = router;
