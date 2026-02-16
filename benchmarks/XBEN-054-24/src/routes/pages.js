const express = require('express');
const { getDatabase } = require('../models/database');
const { marked } = require('marked');

const router = express.Router();

// List all pages
router.get('/', (req, res) => {
  const db = getDatabase();
  const pages = db.prepare(`
    SELECT p.id, p.path, p.title, p.revision, p.updated_at, u.username as creator
    FROM pages p
    LEFT JOIN users u ON p.creator_id = u.id
    ORDER BY p.updated_at DESC
  `).all();

  res.render('page-list', {
    title: 'All Pages',
    pages: pages,
    user: req.user
  });
});

module.exports = router;
