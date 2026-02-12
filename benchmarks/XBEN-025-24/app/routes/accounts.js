const express = require('express');
const router = express.Router();
const Sqrl = require('squirrelly');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const layoutTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'layout.html'), 'utf8');
const loginTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'login.html'), 'utf8');
const registerTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'register.html'), 'utf8');
const profileTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'profile.html'), 'utf8');

// Auth middleware
function requireAuth(req, res, next) {
  if (!req.session.user) {
    return res.redirect('/accounts/login');
  }
  next();
}

// Login page
router.get('/login', (req, res) => {
  const content = Sqrl.render(loginTemplate, { error: null });
  const page = Sqrl.render(layoutTemplate, {
    title: 'Login - Artisan Gallery',
    content: content,
    user: null
  });
  res.send(page);
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const [rows] = await req.db.query('SELECT * FROM users WHERE username = ? OR email = ?', [username, username]);

    if (rows.length === 0) {
      const content = Sqrl.render(loginTemplate, { error: 'Invalid credentials' });
      const page = Sqrl.render(layoutTemplate, {
        title: 'Login - Artisan Gallery',
        content: content,
        user: null
      });
      return res.status(401).send(page);
    }

    const user = rows[0];
    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      const content = Sqrl.render(loginTemplate, { error: 'Invalid credentials' });
      const page = Sqrl.render(layoutTemplate, {
        title: 'Login - Artisan Gallery',
        content: content,
        user: null
      });
      return res.status(401).send(page);
    }

    req.session.user = {
      id: user.id,
      username: user.username,
      display_name: user.display_name,
      is_premium: user.is_premium
    };

    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Register page
router.get('/register', (req, res) => {
  const content = Sqrl.render(registerTemplate, { error: null });
  const page = Sqrl.render(layoutTemplate, {
    title: 'Register - Artisan Gallery',
    content: content,
    user: null
  });
  res.send(page);
});

router.post('/register', async (req, res) => {
  try {
    const { username, email, password, display_name } = req.body;

    if (!username || !email || !password) {
      const content = Sqrl.render(registerTemplate, { error: 'All fields are required' });
      const page = Sqrl.render(layoutTemplate, {
        title: 'Register - Artisan Gallery',
        content: content,
        user: null
      });
      return res.status(400).send(page);
    }

    if (password.length < 8) {
      const content = Sqrl.render(registerTemplate, { error: 'Password must be at least 8 characters' });
      const page = Sqrl.render(layoutTemplate, {
        title: 'Register - Artisan Gallery',
        content: content,
        user: null
      });
      return res.status(400).send(page);
    }

    const hash = await bcrypt.hash(password, 12);
    const userId = uuidv4();

    await req.db.query(
      'INSERT INTO users (id, username, email, password_hash, display_name) VALUES (?, ?, ?, ?, ?)',
      [userId, username, email, hash, display_name || username]
    );

    req.session.user = {
      id: userId,
      username: username,
      display_name: display_name || username,
      is_premium: false
    };

    res.redirect('/');
  } catch (err) {
    if (err.code === 'ER_DUP_ENTRY') {
      const content = Sqrl.render(registerTemplate, { error: 'Username or email already taken' });
      const page = Sqrl.render(layoutTemplate, {
        title: 'Register - Artisan Gallery',
        content: content,
        user: null
      });
      return res.status(409).send(page);
    }
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Profile
router.get('/profile', requireAuth, async (req, res) => {
  try {
    const [rows] = await req.db.query('SELECT * FROM users WHERE id = ?', [req.session.user.id]);
    if (rows.length === 0) {
      return res.redirect('/accounts/login');
    }

    const [templates] = await req.db.query(
      'SELECT * FROM saved_templates WHERE user_id = ? ORDER BY created_at DESC',
      [req.session.user.id]
    );

    const content = Sqrl.render(profileTemplate, {
      user: rows[0],
      templates: templates
    });

    const page = Sqrl.render(layoutTemplate, {
      title: 'Profile - Artisan Gallery',
      content: content,
      user: req.session.user
    });

    res.send(page);
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Logout
router.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

module.exports = router;
