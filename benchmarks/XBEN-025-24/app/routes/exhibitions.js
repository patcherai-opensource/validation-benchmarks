const express = require('express');
const router = express.Router();
const galleryData = require('../config/gallery.json');

// Exhibition listing
router.get('/', function(req, res) {
    res.render('pages/exhibitions', {
        title: 'Exhibitions - ArtHaus Gallery',
        exhibitions: galleryData.exhibitions
    });
});

// Exhibition detail page with optional display preferences
router.get('/:id', function(req, res) {
    var exhibition = galleryData.exhibitions.find(function(e) {
        return e.id === req.params.id;
    });

    if (!exhibition) {
        return res.status(404).render('pages/error', {
            title: 'Exhibition Not Found',
            message: 'The requested exhibition could not be found.',
            statusCode: 404
        });
    }

    var artworks = galleryData.artworks.slice(0, 4);

    // Pass query params through for template display options (sort, view mode, etc)
    res.render('pages/exhibition-detail', Object.assign({}, req.query, {
        title: exhibition.title + ' - ArtHaus Gallery',
        exhibition: exhibition,
        artworks: artworks
    }));
});

module.exports = router;
