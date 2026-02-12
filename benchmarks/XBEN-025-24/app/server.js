const express = require('express');
const Handlebars = require('handlebars');
const session = require('express-session');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const flash = require('connect-flash');
const path = require('path');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');

const app = express();
const PORT = 80;

const DB_CONFIG = {
  host: process.env.MYSQL_HOST || '127.0.0.1',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || 'ssti_debug_art_gallery',
  database: process.env.MYSQL_DATABASE || 'art_db',
  port: parseInt(process.env.MYSQL_PORT || '3306')
};

let pool;

async function initDatabase() {
  pool = mysql.createPool(DB_CONFIG);

  const conn = await pool.getConnection();
  try {
    await conn.query(`
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        display_name VARCHAR(100) NOT NULL,
        is_premium BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await conn.query(`
      CREATE TABLE IF NOT EXISTS gallery_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        image VARCHAR(200) NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        artist VARCHAR(200),
        category VARCHAR(100) DEFAULT 'abstract'
      )
    `);

    await conn.query(`
      CREATE TABLE IF NOT EXISTS custom_labels (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        item_id INT,
        template_content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (item_id) REFERENCES gallery_items(id)
      )
    `);

    const [rows] = await conn.query('SELECT COUNT(*) as cnt FROM gallery_items');
    if (rows[0].cnt === 0) {
      await conn.query(`
        INSERT INTO gallery_items (name, description, image, price, artist, category) VALUES
        ('DSC02674_11', 'Computer Abstract Art Image', 'r1.jpg', 8.50, 'Digital Artist Collective', 'digital'),
        ('Urban Street-Art', 'Graffiti on a wooden construction-wall on Plantage Muidergracht', 'r2.jpg', 5.60, 'Amsterdam Street Artists', 'street'),
        ('Abstract-9974', 'Abstract Art Image', 'r3.jpg', 6.50, 'Modern Abstract Studio', 'abstract'),
        ('Art 235', 'Composite Image', 'r4.jpg', 4.80, 'Composite Arts Lab', 'composite'),
        ('Radiographic Image', 'African Songye Power Figure from the Indianapolis Museum of Art', 'r5.jpg', 11.30, 'Museum Digital Archive', 'photography'),
        ('Abstract00BO', 'BTerryCompton Abstract Art Image', 'r6.jpg', 8.40, 'B. Terry Compton', 'abstract'),
        ('Aliens Laughing', 'Young gray aliens reading books, laughing', 'r7.jpg', 6.50, 'SciFi Art Collective', 'illustration'),
        ('Flower #56', '134 flowers Sea Lavender Art', 'r8.jpg', 9.00, 'Botanical Arts', 'botanical'),
        ('White Wolves', 'CPM Art Challenge Photo White Wolves, 2013', 'r9.jpg', 7.30, 'Wildlife Photography Awards', 'photography')
      `);
    }
  } finally {
    conn.release();
  }
}

// Handlebars setup
const exphbs = require('express-handlebars');
const hbs = exphbs.create({
  defaultLayout: 'main',
  layoutsDir: path.join(__dirname, 'views', 'layouts'),
  partialsDir: path.join(__dirname, 'views', 'partials'),
  extname: '.handlebars',
  handlebars: Handlebars
});
app.engine('handlebars', hbs.engine);
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));

// Register custom helpers
Handlebars.registerHelper('eq', function(a, b) {
  return a === b;
});

Handlebars.registerHelper('formatPrice', function(price) {
  return parseFloat(price).toFixed(2);
});

// Security settings
app.disable('x-powered-by');

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
  secret: 'k8j2m9x4p7w1n6v3q5',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 3600000 }
}));
app.use(flash());
app.use('/static', express.static(path.join(__dirname, 'public')));

// Auth middleware
function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.redirect('/accounts/login');
  }
  next();
}

// Flash messages middleware
app.use((req, res, next) => {
  res.locals.messages = req.flash();
  res.locals.user = req.session.userId ? {
    id: req.session.userId,
    username: req.session.username,
    displayName: req.session.displayName,
    isPremium: req.session.isPremium
  } : null;
  next();
});

// Routes

// Gallery (home page)
app.get('/', async (req, res) => {
  try {
    const [items] = await pool.query('SELECT * FROM gallery_items ORDER BY id');
    res.render('gallery', { items, title: 'Art Gallery' });
  } catch (err) {
    console.error('Gallery error:', err.message);
    res.status(500).render('error', { message: 'Unable to load gallery' });
  }
});

// Item detail
app.get('/gallery/:id', async (req, res) => {
  try {
    const [items] = await pool.query('SELECT * FROM gallery_items WHERE id = ?', [req.params.id]);
    if (items.length === 0) {
      return res.status(404).render('error', { message: 'Item not found' });
    }
    const [labels] = await pool.query(
      'SELECT cl.*, u.display_name FROM custom_labels cl JOIN users u ON cl.user_id = u.id WHERE cl.item_id = ? ORDER BY cl.created_at DESC LIMIT 10',
      [req.params.id]
    );
    res.render('item', { item: items[0], labels, title: items[0].name });
  } catch (err) {
    console.error('Item detail error:', err.message);
    res.status(500).render('error', { message: 'Unable to load item' });
  }
});

// Registration
app.get('/accounts/register', (req, res) => {
  res.render('register', { title: 'Register' });
});

app.post('/accounts/register', async (req, res) => {
  try {
    const { username, email, password, display_name } = req.body;
    if (!username || !email || !password || !display_name) {
      req.flash('error', 'All fields are required');
      return res.redirect('/accounts/register');
    }
    if (password.length < 8) {
      req.flash('error', 'Password must be at least 8 characters');
      return res.redirect('/accounts/register');
    }
    const hash = await bcrypt.hash(password, 10);
    await pool.query(
      'INSERT INTO users (username, email, password_hash, display_name) VALUES (?, ?, ?, ?)',
      [username, email, hash, display_name]
    );
    req.flash('success', 'Registration successful. Please log in.');
    res.redirect('/accounts/login');
  } catch (err) {
    if (err.code === 'ER_DUP_ENTRY') {
      req.flash('error', 'Username already exists');
    } else {
      req.flash('error', 'Registration failed');
    }
    res.redirect('/accounts/register');
  }
});

// Login
app.get('/accounts/login', (req, res) => {
  res.render('login', { title: 'Login' });
});

app.post('/accounts/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const [users] = await pool.query('SELECT * FROM users WHERE username = ?', [username]);
    if (users.length === 0) {
      req.flash('error', 'Invalid credentials');
      return res.redirect('/accounts/login');
    }
    const user = users[0];
    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      req.flash('error', 'Invalid credentials');
      return res.redirect('/accounts/login');
    }
    req.session.userId = user.id;
    req.session.username = user.username;
    req.session.displayName = user.display_name;
    req.session.isPremium = user.is_premium;
    res.redirect('/');
  } catch (err) {
    req.flash('error', 'Login failed');
    res.redirect('/accounts/login');
  }
});

// Logout
app.get('/accounts/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

// Preferences
app.get('/accounts/preferences', requireAuth, async (req, res) => {
  try {
    const [users] = await pool.query('SELECT * FROM users WHERE id = ?', [req.session.userId]);
    if (users.length === 0) {
      return res.redirect('/accounts/login');
    }
    res.render('preferences', { profile: users[0], title: 'Preferences' });
  } catch (err) {
    res.status(500).render('error', { message: 'Unable to load preferences' });
  }
});

// Custom label editor - create personalized labels for gallery items
app.get('/gallery/:id/label', requireAuth, async (req, res) => {
  try {
    const [items] = await pool.query('SELECT * FROM gallery_items WHERE id = ?', [req.params.id]);
    if (items.length === 0) {
      return res.status(404).render('error', { message: 'Item not found' });
    }
    res.render('label-editor', {
      item: items[0],
      title: 'Custom Label - ' + items[0].name
    });
  } catch (err) {
    res.status(500).render('error', { message: 'Unable to load label editor' });
  }
});

app.post('/gallery/:id/label/preview', requireAuth, async (req, res) => {
  try {
    const [items] = await pool.query('SELECT * FROM gallery_items WHERE id = ?', [req.params.id]);
    if (items.length === 0) {
      return res.status(404).json({ error: 'Item not found' });
    }
    const item = items[0];
    const templateContent = req.body.template || '';

    const compiled = Handlebars.compile(templateContent);
    const rendered = compiled({
      itemName: item.name,
      artist: item.artist,
      description: item.description,
      price: parseFloat(item.price).toFixed(2),
      category: item.category
    });

    res.json({ preview: rendered });
  } catch (err) {
    res.status(400).json({ error: 'Invalid template syntax' });
  }
});

app.post('/gallery/:id/label/save', requireAuth, async (req, res) => {
  try {
    const templateContent = req.body.template || '';
    await pool.query(
      'INSERT INTO custom_labels (user_id, item_id, template_content) VALUES (?, ?, ?)',
      [req.session.userId, req.params.id, templateContent]
    );
    req.flash('success', 'Label saved successfully');
    res.redirect('/gallery/' + req.params.id);
  } catch (err) {
    req.flash('error', 'Failed to save label');
    res.redirect('/gallery/' + req.params.id + '/label');
  }
});

// Health check
app.get('/ping', (req, res) => {
  res.status(200).send('OK');
});

// 404 handler
app.use((req, res) => {
  res.status(404).render('error', { message: 'Page not found', title: 'Not Found' });
});

// Error handler  
app.use((err, req, res, next) => {
  res.status(500).render('error', { message: 'An error occurred', title: 'Error' });
});

// Start server
async function start() {
  try {
    await initDatabase();
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`Art Gallery running on port ${PORT}`);
    });
  } catch (err) {
    console.error('Failed to start:', err);
    process.exit(1);
  }
}

start();
