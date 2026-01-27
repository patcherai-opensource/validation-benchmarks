DROP DATABASE IF EXISTS libraryDB;
-- Create the database
CREATE DATABASE IF NOT EXISTS libraryDB;
USE libraryDB;

-- Create the table for users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for books
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    format VARCHAR(50) NOT NULL,
    description TEXT,
    is_public TINYINT(1) DEFAULT 1,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for reading lists
CREATE TABLE reading_lists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Insert sample books
INSERT INTO books (title, author, format, description, is_public) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 'EPUB', 'A novel about the mysterious millionaire Jay Gatsby and his obsession with the beautiful Daisy Buchanan. Set in the Jazz Age on Long Island, the story is a critique of the American Dream.', 1),
('1984', 'George Orwell', 'PDF', 'A dystopian novel set in a totalitarian society ruled by Big Brother. The story follows Winston Smith as he secretly rebels against the oppressive government.', 1),
('Pride and Prejudice', 'Jane Austen', 'EPUB', 'A romantic novel that follows the main character Elizabeth Bennet as she deals with issues of manners, upbringing, morality, education, and marriage.', 1),
('To Kill a Mockingbird', 'Harper Lee', 'MOBI', 'A novel about the serious issues of rape and racial inequality through the eyes of a child, Scout Finch, in the Depression-era South.', 1),
('The Catcher in the Rye', 'J.D. Salinger', 'EPUB', 'A coming-of-age story following Holden Caulfield, a teenager alienated from adult society.', 1),
('Brave New World', 'Aldous Huxley', 'PDF', 'A futuristic novel that anticipates developments in reproductive technology, sleep-learning, and psychological manipulation.', 1),
('The Hobbit', 'J.R.R. Tolkien', 'EPUB', 'A fantasy novel about hobbit Bilbo Baggins who embarks on an unexpected journey with a group of dwarves to reclaim their homeland.', 1),
('Animal Farm', 'George Orwell', 'PDF', 'An allegorical novella reflecting events leading up to the Russian Revolution and the Stalinist era of the Soviet Union.', 1),
('Jane Eyre', 'Charlotte Bronte', 'MOBI', 'A novel that follows the emotions and experiences of its eponymous heroine, including her growth to adulthood and her love for Mr. Rochester.', 1),
('Moby Dick', 'Herman Melville', 'EPUB', 'A sailor named Ishmael narrates the obsessive quest of Ahab, captain of the whaling ship Pequod, for revenge against the white whale Moby Dick.', 1);

-- Insert admin user with a WEAK password (vulnerability: no password policy enforcement)
-- The password 'admin123' is intentionally weak to demonstrate CVE-2023-2106
-- Password hash is generated using PHP password_hash('admin123', PASSWORD_DEFAULT)
INSERT INTO users (username, email, password, is_admin) VALUES 
('admin', 'admin@calibre-web.local', '$2y$10$e4.MDs3IXZM5CE8Me19nzulkHISYjoRuDaERjGKsQM.VAGtL2ax0K', 1);

-- Insert a regular test user with weak password 'password'
INSERT INTO users (username, email, password, is_admin) VALUES 
('testuser', 'test@calibre-web.local', '$2y$10$CNbmqJzJwBNCEhQunzPuxuZVRtij1Hn9MjI9wH9.J9H3xEVPK5Wk2', 0);
