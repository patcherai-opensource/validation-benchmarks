const express = require('express');
const router = express.Router();
const Sqrl = require('squirrelly');
const path = require('path');
const fs = require('fs');

// Load layout template
const layoutTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'layout.html'), 'utf8');
const galleryTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'gallery.html'), 'utf8');
const artworkTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'artwork.html'), 'utf8');

// Home / Gallery page
router.get('/', async (req, res) => {
  try {
    const [artworks] = await req.db.query('SELECT * FROM artworks ORDER BY created_at DESC');
    const user = req.session.user || null;

    const content = Sqrl.render(galleryTemplate, {
      artworks: artworks,
      user: user
    });

    const page = Sqrl.render(layoutTemplate, {
      title: 'Artisan Gallery',
      content: content,
      user: user
    });

    res.send(page);
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Single artwork view
router.get('/artwork/:id', async (req, res) => {
  try {
    const [rows] = await req.db.query('SELECT * FROM artworks WHERE id = ?', [req.params.id]);
    if (rows.length === 0) {
      return res.status(404).send('Artwork not found');
    }

    const user = req.session.user || null;
    const content = Sqrl.render(artworkTemplate, {
      artwork: rows[0],
      user: user
    });

    const page = Sqrl.render(layoutTemplate, {
      title: rows[0].title + ' - Artisan Gallery',
      content: content,
      user: user
    });

    res.send(page);
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Health check
router.get('/ping', (req, res) => {
  res.status(200).send('OK');
});

module.exports = router;
