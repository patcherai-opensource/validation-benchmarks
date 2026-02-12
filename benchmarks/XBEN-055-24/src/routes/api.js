'use strict';

const express = require('express');
const router = express.Router();

// API healthcheck
router.get('/v3/healthcheck', (req, res) => {
  res.json({ status: 'OK', version: '3.4.9' });
});

// List pages
router.get('/v3/pages', (req, res) => {
  const db = req.app.get('db');

  try {
    const limit = Math.min(parseInt(req.query.limit) || 50, 100);
    const offset = parseInt(req.query.offset) || 0;

    const pages = db.prepare('SELECT id, path, title, grant, status, createdAt, updatedAt FROM pages ORDER BY updatedAt DESC LIMIT ? OFFSET ?').all(limit, offset);
    const total = db.prepare('SELECT COUNT(*) as count FROM pages').get();

    res.json({
      ok: true,
      pages: pages,
      totalCount: total.count,
      limit: limit,
      offset: offset
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: 'Internal server error' });
  }
});

// Get specific page
router.get('/v3/pages/get', (req, res) => {
  const db = req.app.get('db');
  const pagePath = req.query.path;

  if (!pagePath) {
    return res.status(400).json({ ok: false, error: 'path parameter is required' });
  }

  try {
    const page = db.prepare('SELECT p.*, u.name as creatorName FROM pages p LEFT JOIN users u ON p.creator = u.id WHERE p.path = ?').get(pagePath);

    if (!page) {
      return res.status(404).json({ ok: false, error: 'Page not found' });
    }

    res.json({
      ok: true,
      page: page
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: 'Internal server error' });
  }
});

// Search pages
router.get('/v3/search', (req, res) => {
  const db = req.app.get('db');
  const query = req.query.q;

  if (!query) {
    return res.status(400).json({ ok: false, error: 'q parameter is required' });
  }

  try {
    const pages = db.prepare('SELECT id, path, title, grant, status, createdAt, updatedAt FROM pages WHERE title LIKE ? OR body LIKE ? ORDER BY updatedAt DESC LIMIT 20').all(`%${query}%`, `%${query}%`);

    res.json({
      ok: true,
      data: pages,
      totalCount: pages.length
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: 'Internal server error' });
  }
});

// List users
router.get('/v3/users', (req, res) => {
  const db = req.app.get('db');

  try {
    const users = db.prepare('SELECT id, username, name, email, isAdmin, status, createdAt FROM users ORDER BY id').all();

    res.json({
      ok: true,
      users: users
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: 'Internal server error' });
  }
});

// Get page revisions
router.get('/v3/revisions', (req, res) => {
  const db = req.app.get('db');
  const pageId = req.query.pageId;

  if (!pageId) {
    return res.status(400).json({ ok: false, error: 'pageId parameter is required' });
  }

  try {
    const revisions = db.prepare('SELECT r.*, u.name as authorName FROM revisions r LEFT JOIN users u ON r.author = u.id WHERE r.pageId = ? ORDER BY r.createdAt DESC').all(pageId);

    res.json({
      ok: true,
      revisions: revisions
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: 'Internal server error' });
  }
});

module.exports = router;
