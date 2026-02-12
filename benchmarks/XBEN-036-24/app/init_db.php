<?php
// Initialize SQLite database for guest entries

$dbDir = '/var/db';
if (!is_dir($dbDir)) {
    mkdir($dbDir, 0755, true);
}

$db = new PDO('sqlite:/var/db/entries.sqlite');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Create collections table
$db->exec("CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    handle TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    allow_uploads INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)");

// Create entries table
$db->exec("CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_handle TEXT NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    content TEXT,
    author_name TEXT,
    author_email TEXT,
    featured_image TEXT,
    attachment TEXT,
    status TEXT DEFAULT 'draft',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_handle) REFERENCES collections(handle)
)");

// Seed collections
$db->exec("INSERT OR IGNORE INTO collections (handle, title, description, allow_uploads) VALUES
    ('blog', 'Blog Posts', 'Community blog posts submitted by guests', 1),
    ('testimonials', 'Testimonials', 'Customer testimonials and reviews', 1),
    ('events', 'Events', 'Community event submissions', 0)
");

// Seed some sample entries
$db->exec("INSERT OR IGNORE INTO entries (collection_handle, title, slug, content, author_name, author_email, status) VALUES
    ('blog', 'Welcome to Our Community', 'welcome-to-our-community', 'We are excited to launch our new community platform. Share your stories and experiences with us!', 'Admin', 'admin@example.com', 'published'),
    ('blog', 'Tips for Better Writing', 'tips-for-better-writing', 'Here are some practical tips to improve your writing skills...', 'Jane Smith', 'jane@example.com', 'published'),
    ('testimonials', 'Great Service!', 'great-service', 'The team was incredibly helpful and responsive. Highly recommended!', 'John Doe', 'john@example.com', 'published'),
    ('testimonials', 'Five Stars', 'five-stars', 'Best experience I have had with any service provider. Will definitely come back.', 'Sarah Johnson', 'sarah@example.com', 'published'),
    ('events', 'Annual Community Meetup 2024', 'annual-community-meetup-2024', 'Join us for our annual community meetup this spring.', 'Events Team', 'events@example.com', 'published')
");

echo "Database initialized successfully.\n";
?>