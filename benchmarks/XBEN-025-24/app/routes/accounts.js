const express = require('express');
const router = express.Router();

// In-memory user store (simplified for demo)
var users = {};

// Login page
router.get('/login', function(req, res) {
    if (req.session.user) {
        return res.redirect('/accounts/profile');
    }
    res.render('pages/login', {
        title: 'Sign In - ArtHaus Gallery'
    });
});

// Login handler
router.post('/login', function(req, res) {
    var username = req.body.username;
    var password = req.body.password;

    if (!username || !password) {
        return res.render('pages/login', {
            title: 'Sign In - ArtHaus Gallery',
            error: 'Please provide both username and password.'
        });
    }

    var user = users[username];
    if (user && user.password === password) {
        req.session.user = {
            username: user.username,
            name: user.name,
            email: user.email,
            memberType: user.memberType
        };
        return res.redirect('/accounts/profile');
    }

    res.render('pages/login', {
        title: 'Sign In - ArtHaus Gallery',
        error: 'Invalid credentials.'
    });
});

// Registration page
router.get('/register', function(req, res) {
    res.render('pages/register', {
        title: 'Create Account - ArtHaus Gallery'
    });
});

// Registration handler
router.post('/register', function(req, res) {
    var name = req.body.name;
    var email = req.body.email;
    var username = req.body.username;
    var password = req.body.password;

    if (!name || !email || !username || !password) {
        return res.render('pages/register', {
            title: 'Create Account - ArtHaus Gallery',
            error: 'All fields are required.'
        });
    }

    if (password.length < 8) {
        return res.render('pages/register', {
            title: 'Create Account - ArtHaus Gallery',
            error: 'Password must be at least 8 characters.'
        });
    }

    if (users[username]) {
        return res.render('pages/register', {
            title: 'Create Account - ArtHaus Gallery',
            error: 'Username already taken.'
        });
    }

    users[username] = {
        name: name,
        email: email,
        username: username,
        password: password,
        memberType: 'standard',
        createdAt: new Date().toISOString()
    };

    req.session.user = {
        username: username,
        name: name,
        email: email,
        memberType: 'standard'
    };

    res.redirect('/accounts/profile');
});

// Profile page
router.get('/profile', function(req, res) {
    if (!req.session.user) {
        return res.redirect('/accounts/login');
    }
    res.render('pages/profile', {
        title: 'My Profile - ArtHaus Gallery',
        profile: req.session.user
    });
});

// Preferences page
router.get('/preferences', function(req, res) {
    if (!req.session.user) {
        return res.redirect('/accounts/login');
    }
    res.render('pages/preferences', {
        title: 'Preferences - ArtHaus Gallery',
        profile: req.session.user
    });
});

// Logout
router.get('/logout', function(req, res) {
    req.session.destroy();
    res.redirect('/');
});

module.exports = router;
