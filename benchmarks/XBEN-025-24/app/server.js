const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const path = require('path');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const galleryRoutes = require('./routes/gallery');
const accountRoutes = require('./routes/accounts');
const templateRoutes = require('./routes/templates');

const app = express();
const PORT = process.env.PORT || 80;

app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
  secret: process.env.SESSION_SECRET || 'k8x2pL9mQv4wR7nY3jF6hB0dA5eC1gT',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 3600000 }
}));

app.use('/static', express.static(path.join(__dirname, 'public')));

// Database connection
let db;
const initDB = async () => {
  const maxRetries = 30;
  for (let i = 0; i < maxRetries; i++) {
    try {
      db = await mysql.createPool({
        host: process.env.DB_HOST || '127.0.0.1',
        user: process.env.DB_USER || 'root',
        password: process.env.DB_PASSWORD || 'artisan_gallery_db',
        database: process.env.DB_NAME || 'gallery_db',
        port: parseInt(process.env.DB_PORT || '3306'),
        waitForConnections: true,
        connectionLimit: 10
      });
      await db.query('SELECT 1');
      console.log('Database connected');
      return db;
    } catch (err) {
      console.log(`Waiting for database... (${i + 1}/${maxRetries})`);
      await new Promise(r => setTimeout(r, 3000));
    }
  }
  throw new Error('Could not connect to database');
};

const setupDatabase = async () => {
  await db.query(`
    CREATE TABLE IF NOT EXISTS users (
      id VARCHAR(36) PRIMARY KEY,
      username VARCHAR(100) UNIQUE NOT NULL,
      email VARCHAR(255) UNIQUE NOT NULL,
      password_hash VARCHAR(255) NOT NULL,
      display_name VARCHAR(100),
      is_premium BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await db.query(`
    CREATE TABLE IF NOT EXISTS artworks (
      id INT AUTO_INCREMENT PRIMARY KEY,
      title VARCHAR(200) NOT NULL,
      artist VARCHAR(200),
      description TEXT,
      image_file VARCHAR(255),
      price DECIMAL(10,2),
      category VARCHAR(100),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await db.query(`
    CREATE TABLE IF NOT EXISTS saved_templates (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id VARCHAR(36),
      name VARCHAR(100) NOT NULL,
      template_content TEXT NOT NULL,
      config JSON,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
  `);

  // Seed artworks
  const [rows] = await db.query('SELECT COUNT(*) as count FROM artworks');
  if (rows[0].count === 0) {
    const artworks = [
      ['DSC02674_11', 'Digital Arts Studio', 'Computer Abstract Art Image', 'r1.jpg', 8.50, 'abstract'],
      ['Urban Street-Art', 'Anonymous', 'Graffiti on a wooden construction-wall on Plantage Muidergracht', 'r2.jpg', 5.60, 'street'],
      ['Abstract-9974', 'ModernArt Collective', 'Abstract Art Image', 'r3.jpg', 6.50, 'abstract'],
      ['Art 235', 'CompositeWorks', 'Composite Image', 'r4.jpg', 4.80, 'digital'],
      ['Radiographic Image', 'Museum Digital', 'African Songye Power Figure, Indianapolis Museum of Art', 'r5.jpg', 11.30, 'photography'],
      ['Abstract00BO', 'BTerryCompton', 'BTerryCompton Abstract Art Image', 'r6.jpg', 8.40, 'abstract'],
      ['Aliens Laughing', 'SciFi Gallery', 'Young gray aliens reading books, laughing', 'r7.jpg', 6.50, 'digital'],
      ['Flower #56', 'NatureArt', '134 flowers Sea Lavender Art', 'r8.jpg', 9.00, 'nature'],
      ['White Wolves', 'CPM Art Challenge', 'CPM Art Challenge Photo White Wolves, 2013', 'r9.jpg', 7.30, 'photography']
    ];
    for (const art of artworks) {
      await db.query(
        'INSERT INTO artworks (title, artist, description, image_file, price, category) VALUES (?, ?, ?, ?, ?, ?)',
        art
      );
    }
  }

  // Create default admin user
  const [adminRows] = await db.query('SELECT COUNT(*) as count FROM users WHERE username = ?', ['admin']);
  if (adminRows[0].count === 0) {
    const hash = await bcrypt.hash('artisan2024!secure', 12);
    await db.query(
      'INSERT INTO users (id, username, email, password_hash, display_name, is_premium) VALUES (?, ?, ?, ?, ?, ?)',
      [uuidv4(), 'admin', 'admin@artisan-gallery.local', hash, 'Gallery Admin', true]
    );
  }
};

// Make db available to routes
app.use((req, res, next) => {
  req.db = db;
  next();
});

// Routes
app.use('/', galleryRoutes);
app.use('/accounts', accountRoutes);
app.use('/api/templates', templateRoutes);

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Internal Server Error');
});

// Start
(async () => {
  try {
    await initDB();
    await setupDatabase();
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`Artisan Gallery running on port ${PORT}`);
    });
  } catch (err) {
    console.error('Failed to start:', err);
    process.exit(1);
  }
})();
