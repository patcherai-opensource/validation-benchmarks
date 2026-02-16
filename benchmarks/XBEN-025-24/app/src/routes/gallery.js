const express = require('express');
const router = express.Router();
const { getDb } = require('../models/database');

router.get('/', (req, res) => {
  const db = getDb();
  const artworks = db.prepare('SELECT * FROM artworks ORDER BY id').all();
  res.render('gallery', {
    title: 'ArtSpace Gallery',
    artworks: artworks
  });
});

router.get('/artwork/:id', (req, res) => {
  const db = getDb();
  const artwork = db.prepare('SELECT * FROM artworks WHERE id = ?').get(req.params.id);
  if (!artwork) {
    return res.status(404).render('error', {
      title: 'Not Found',
      message: 'Artwork not found.'
    });
  }
  res.render('artwork-detail', {
    title: artwork.title,
    artwork: artwork
  });
});

module.exports = router;
