const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const path = require('path');

const DB_PATH = path.join(__dirname, '..', 'data', 'artspace.db');

let db;

function getDb() {
  if (!db) {
    const fs = require('fs');
    const dir = path.dirname(DB_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
  }
  return db;
}

function initialize() {
  const conn = getDb();

  conn.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      display_name TEXT NOT NULL,
      is_premium INTEGER DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  conn.exec(`
    CREATE TABLE IF NOT EXISTS artworks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT,
      image_file TEXT NOT NULL,
      price REAL NOT NULL,
      artist_name TEXT,
      category TEXT DEFAULT 'general',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  conn.exec(`
    CREATE TABLE IF NOT EXISTS greeting_cards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      card_name TEXT NOT NULL,
      template_body TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  const artCount = conn.prepare('SELECT COUNT(*) as cnt FROM artworks').get();
  if (artCount.cnt === 0) {
    const insertArt = conn.prepare(
      'INSERT INTO artworks (title, description, image_file, price, artist_name, category) VALUES (?, ?, ?, ?, ?, ?)'
    );
    const artworks = [
      ['DSC02674_11', 'Computer Abstract Art Image', 'r1.jpg', 8.50, 'Digital Arts Collective', 'digital'],
      ['Urban Street-Art', 'Graffiti on a wooden construction-wall on Plantage Muidergracht', 'r2.jpg', 5.60, 'Amsterdam Street Artists', 'street'],
      ['Abstract-9974', 'Abstract Art Image', 'r3.jpg', 6.50, 'Modern Impressions Studio', 'abstract'],
      ['Art 235', 'Composite Image', 'r4.jpg', 4.80, 'Composite Works Ltd', 'mixed'],
      ['Radiographic Image', 'African Songye Power Figure - Indianapolis Museum of Art', 'r5.jpg', 11.30, 'Museum Collections', 'photography'],
      ['Abstract00BO', 'BTerryCompton Abstract Art Image', 'r6.jpg', 8.40, 'B. Terry Compton', 'abstract'],
      ['Aliens Laughing', 'Young gray aliens reading books, laughing', 'r7.jpg', 6.50, 'Sci-Fi Illustrations', 'digital'],
      ['Flower #56', '134 Flowers Sea Lavender Art', 'r8.jpg', 9.00, 'Botanical Arts', 'nature'],
      ['White Wolves', 'CPM Art Challenge Photo White Wolves, 2013', 'r9.jpg', 7.30, 'Wildlife Photography Assoc.', 'photography']
    ];
    const insertMany = conn.transaction((items) => {
      for (const item of items) {
        insertArt.run(...item);
      }
    });
    insertMany(artworks);
  }

  const defaultCards = conn.prepare('SELECT COUNT(*) as cnt FROM greeting_cards WHERE user_id IS NULL').get();
  if (defaultCards.cnt === 0) {
    const insertCard = conn.prepare(
      'INSERT INTO greeting_cards (user_id, card_name, template_body) VALUES (?, ?, ?)'
    );
    const cards = [
      [null, 'Welcome Card', '<div class="card-body"><h3>Welcome, {{recipientName}}!</h3><p>Thank you for joining ArtSpace Gallery.</p></div>'],
      [null, 'Birthday Card', '<div class="card-body"><h3>Happy Birthday, {{recipientName}}!</h3><p>Wishing you a wonderful day filled with art and joy.</p></div>'],
      [null, 'Thank You Card', '<div class="card-body"><h3>Thank You, {{recipientName}}!</h3><p>We appreciate your continued support of independent artists.</p></div>']
    ];
    const insertMany = conn.transaction((items) => {
      for (const item of items) {
        insertCard.run(...item);
      }
    });
    insertMany(cards);
  }
}

module.exports = { getDb, initialize };
