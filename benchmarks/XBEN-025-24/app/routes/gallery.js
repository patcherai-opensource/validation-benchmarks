const express = require('express');
const router = express.Router();
const path = require('path');
const galleryData = require('../config/gallery.json');

// Home page - Gallery listing
router.get('/', function(req, res) {
    var featured = galleryData.artworks.slice(0, 6);
    var collections = galleryData.collections.filter(function(c) { return c.featured; });

    res.render('pages/home', {
        title: 'ArtHaus Gallery',
        artworks: featured,
        collections: collections,
        activeExhibition: galleryData.exhibitions.find(function(e) { return e.active; })
    });
});

// Browse all artworks
router.get('/browse', function(req, res) {
    var collection = req.query.collection;
    var artworks = galleryData.artworks;

    if (collection) {
        artworks = artworks.filter(function(a) { return a.collection === collection; });
    }

    res.render('pages/browse', {
        title: 'Browse Collection',
        artworks: artworks,
        collections: galleryData.collections,
        selectedCollection: collection || 'all'
    });
});

// Single artwork detail
router.get('/artwork/:id', function(req, res) {
    var artwork = galleryData.artworks.find(function(a) {
        return a.id === parseInt(req.params.id);
    });

    if (!artwork) {
        return res.status(404).render('pages/error', {
            title: 'Artwork Not Found',
            message: 'The requested artwork could not be found.',
            statusCode: 404
        });
    }

    // Get related artworks from same collection
    var related = galleryData.artworks.filter(function(a) {
        return a.collection === artwork.collection && a.id !== artwork.id;
    }).slice(0, 3);

    res.render('pages/artwork', {
        title: artwork.title + ' - ArtHaus Gallery',
        artwork: artwork,
        related: related
    });
});

// Collection page
router.get('/collection/:id', function(req, res) {
    var collection = galleryData.collections.find(function(c) {
        return c.id === req.params.id;
    });

    if (!collection) {
        return res.status(404).render('pages/error', {
            title: 'Collection Not Found',
            message: 'The requested collection could not be found.',
            statusCode: 404
        });
    }

    var artworks = galleryData.artworks.filter(function(a) {
        return a.collection === collection.id;
    });

    res.render('pages/collection', {
        title: collection.name + ' - ArtHaus Gallery',
        collection: collection,
        artworks: artworks
    });
});

// About page
router.get('/about', function(req, res) {
    res.render('pages/about', {
        title: 'About - ArtHaus Gallery'
    });
});

module.exports = router;
