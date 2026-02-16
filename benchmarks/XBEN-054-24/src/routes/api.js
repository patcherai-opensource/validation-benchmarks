const express = require('express');
const { getDatabase } = require('../models/database');

const router = express.Router();

// List pages
router.get('/pages', (req, res) => {
  const db = getDatabase();
  const pages = db.prepare(`
    SELECT p.id, p.path, p.title, p.revision, p.updated_at
    FROM pages p
    ORDER BY p.updated_at DESC
  `).all();

  res.json({ pages });
});

// Get single page
router.get('/pages/:id', (req, res) => {
  const db = getDatabase();
  const page = db.prepare(`
    SELECT p.*, u.username as creator_name
    FROM pages p
    LEFT JOIN users u ON p.creator_id = u.id
    WHERE p.id = ?
  `).get(req.params.id);

  if (!page) {
    return res.status(404).json({ error: 'Page not found' });
  }

  res.json({ page });
});

// Search pages
router.get('/search', (req, res) => {
  const q = req.query.q || '';
  if (!q) {
    return res.json({ results: [] });
  }

  const db = getDatabase();
  const results = db.prepare(`
    SELECT p.id, p.path, p.title, p.updated_at
    FROM pages p
    WHERE p.title LIKE ? OR p.body LIKE ?
    ORDER BY p.updated_at DESC
    LIMIT 20
  `).all(`%${q}%`, `%${q}%`);

  res.json({ results });
});

// List users (basic info)
router.get('/users', (req, res) => {
  const db = getDatabase();
  const users = db.prepare(`
    SELECT id, username, role, status, created_at
    FROM users
  `).all();

  res.json({ users });
});

// Get page revisions
router.get('/revisions/:pageId', (req, res) => {
  const db = getDatabase();
  const revisions = db.prepare(`
    SELECT r.id, r.revision_number, r.created_at, u.username as author
    FROM revisions r
    LEFT JOIN users u ON r.author_id = u.id
    WHERE r.page_id = ?
    ORDER BY r.revision_number DESC
  `).all(req.params.pageId);

  res.json({ revisions });
});

// Get page comments
router.get('/comments/:pageId', (req, res) => {
  const db = getDatabase();
  const comments = db.prepare(`
    SELECT c.id, c.body, c.created_at, u.username as author
    FROM comments c
    LEFT JOIN users u ON c.author_id = u.id
    WHERE c.page_id = ?
    ORDER BY c.created_at DESC
  `).all(req.params.pageId);

  res.json({ comments });
});

module.exports = router;
