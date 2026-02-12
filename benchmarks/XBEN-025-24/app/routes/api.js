const express = require('express');
const router = express.Router();
const galleryData = require('../config/gallery.json');

// API: Get all artworks
router.get('/artworks', function(req, res) {
    var collection = req.query.collection;
    var artworks = galleryData.artworks;

    if (collection) {
        artworks = artworks.filter(function(a) { return a.collection === collection; });
    }

    res.json({
        status: 'ok',
        count: artworks.length,
        data: artworks.map(function(a) {
            return {
                id: a.id,
                title: a.title,
                artist: a.artist,
                price: a.price,
                collection: a.collection,
                image: '/static/img/' + a.image
            };
        })
    });
});

// API: Get single artwork
router.get('/artworks/:id', function(req, res) {
    var artwork = galleryData.artworks.find(function(a) {
        return a.id === parseInt(req.params.id);
    });

    if (!artwork) {
        return res.status(404).json({ status: 'error', message: 'Artwork not found' });
    }

    res.json({ status: 'ok', data: artwork });
});

// API: Get collections
router.get('/collections', function(req, res) {
    res.json({
        status: 'ok',
        data: galleryData.collections
    });
});

// API: Get exhibitions
router.get('/exhibitions', function(req, res) {
    res.json({
        status: 'ok',
        data: galleryData.exhibitions
    });
});

module.exports = router;
