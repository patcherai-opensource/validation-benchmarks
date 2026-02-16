const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const { getDb } = require('../models/database');

router.get('/register', (req, res) => {
  res.render('register', { title: 'Register' });
});

router.post('/register', (req, res) => {
  const { username, email, password, display_name } = req.body;

  if (!username || !email || !password || !display_name) {
    return res.render('register', {
      title: 'Register',
      errorMessage: 'All fields are required.'
    });
  }

  if (password.length < 8) {
    return res.render('register', {
      title: 'Register',
      errorMessage: 'Password must be at least 8 characters.'
    });
  }

  const db = getDb();

  const existing = db.prepare('SELECT id FROM users WHERE username = ? OR email = ?').get(username, email);
  if (existing) {
    return res.render('register', {
      title: 'Register',
      errorMessage: 'Username or email already exists.'
    });
  }

  const hash = bcrypt.hashSync(password, 10);
  const result = db.prepare(
    'INSERT INTO users (username, email, password_hash, display_name) VALUES (?, ?, ?, ?)'
  ).run(username, email, hash, display_name);

  req.session.user = {
    id: result.lastInsertRowid,
    username: username,
    email: email,
    display_name: display_name,
    is_premium: 0
  };

  res.redirect('/');
});

router.get('/login', (req, res) => {
  res.render('login', { title: 'Login' });
});

router.post('/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.render('login', {
      title: 'Login',
      errorMessage: 'Username and password are required.'
    });
  }

  const db = getDb();
  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);

  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return res.render('login', {
      title: 'Login',
      errorMessage: 'Invalid credentials.'
    });
  }

  req.session.user = {
    id: user.id,
    username: user.username,
    email: user.email,
    display_name: user.display_name,
    is_premium: user.is_premium
  };

  res.redirect('/');
});

router.get('/profile', (req, res) => {
  if (!req.session.user) {
    return res.redirect('/accounts/login');
  }
  res.render('profile', {
    title: 'Profile',
    profile: req.session.user
  });
});

router.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

module.exports = router;
