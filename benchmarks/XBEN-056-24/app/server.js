const express = require('express');
const { engine } = require('express-handlebars');
const Handlebars = require('handlebars');
const session = require('express-session');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Read flag from file or environment
const FLAG = process.env.FLAG || (fs.existsSync('/flag.txt') ? fs.readFileSync('/flag.txt', 'utf8').trim() : 'FLAG{default}');

// Database connection
let db;
const connectDB = async () => {
    const maxRetries = 30;
    for (let i = 0; i < maxRetries; i++) {
        try {
            db = await mysql.createPool({
                host: process.env.DB_HOST || 'localhost',
                user: process.env.DB_USER || 'root',
                password: process.env.DB_PASSWORD || 'eventboard_db_pass',
                database: process.env.DB_NAME || 'eventboard_db',
                waitForConnections: true,
                connectionLimit: 10
            });
            console.log('Connected to MySQL');
            await initDB();
            return;
        } catch (err) {
            console.log(`Database connection attempt ${i + 1}/${maxRetries} failed, retrying...`);
            await new Promise(r => setTimeout(r, 2000));
        }
    }
    console.error('Failed to connect to database after retries');
    process.exit(1);
};

const initDB = async () => {
    try {
        // Create users table
        await db.query(`
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) NOT NULL,
                display_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
        
        // Create events table
        await db.query(`
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                event_date DATE,
                location VARCHAR(255),
                organizer_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Create feedback table
        await db.query(`
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT,
                user_name VARCHAR(255),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Insert sample events
        await db.query(`
            INSERT IGNORE INTO events (id, title, description, event_date, location, organizer_id) VALUES
            (1, 'Tech Meetup 2024', 'Annual technology conference featuring latest innovations', '2024-06-15', 'Downtown Convention Center', 1),
            (2, 'Art Exhibition Opening', 'Contemporary art showcase from local artists', '2024-05-20', 'City Art Gallery', 1),
            (3, 'Community Cleanup Day', 'Volunteer event to clean up local parks', '2024-04-22', 'Central Park', 2),
            (4, 'Music Festival', 'Three-day outdoor music event', '2024-07-04', 'Riverside Amphitheater', 1),
            (5, 'Coding Workshop', 'Learn web development basics', '2024-05-10', 'Tech Hub Building', 2)
        `);

        console.log('Database initialized');
    } catch (err) {
        console.error('Database init error:', err);
    }
};

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
    secret: 'eventboard-session-key-2024',
    resave: false,
    saveUninitialized: true
}));

// Setup Handlebars with vulnerable configuration
app.engine('hbs', engine({
    extname: '.hbs',
    defaultLayout: 'main',
    layoutsDir: path.join(__dirname, 'views/layouts'),
    partialsDir: path.join(__dirname, 'views/partials'),
    handlebars: Handlebars
}));
app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'views'));

// Routes
app.get('/', async (req, res) => {
    try {
        const [events] = await db.query('SELECT * FROM events ORDER BY event_date ASC LIMIT 6');
        res.render('home', { 
            events,
            user: req.session.user,
            title: 'EventBoard - Community Events'
        });
    } catch (err) {
        res.render('home', { events: [], title: 'EventBoard - Community Events' });
    }
});

app.get('/events', async (req, res) => {
    try {
        const [events] = await db.query('SELECT * FROM events ORDER BY event_date ASC');
        res.render('events', { 
            events,
            user: req.session.user,
            title: 'All Events'
        });
    } catch (err) {
        res.render('events', { events: [], title: 'All Events' });
    }
});

app.get('/event/:id', async (req, res) => {
    try {
        const [events] = await db.query('SELECT * FROM events WHERE id = ?', [req.params.id]);
        const [feedback] = await db.query('SELECT * FROM feedback WHERE event_id = ? ORDER BY created_at DESC', [req.params.id]);
        
        if (events.length === 0) {
            return res.status(404).render('error', { message: 'Event not found' });
        }
        
        res.render('event-detail', {
            event: events[0],
            feedback,
            user: req.session.user,
            title: events[0].title
        });
    } catch (err) {
        res.status(500).render('error', { message: 'Database error' });
    }
});

// Feedback submission
app.post('/event/:id/feedback', async (req, res) => {
    const { user_name, message } = req.body;
    const eventId = req.params.id;
    
    try {
        await db.query(
            'INSERT INTO feedback (event_id, user_name, message) VALUES (?, ?, ?)',
            [eventId, user_name, message]
        );
        res.redirect(`/event/${eventId}`);
    } catch (err) {
        res.status(500).render('error', { message: 'Failed to submit feedback' });
    }
});

// Badge preview - VULNERABLE ENDPOINT
// User-provided template content is compiled and rendered via Handlebars
app.get('/badge/preview', async (req, res) => {
    const { name, event_id } = req.query;
    
    if (!name || !event_id) {
        return res.status(400).json({ error: 'Missing name or event_id parameter' });
    }
    
    try {
        const [events] = await db.query('SELECT * FROM events WHERE id = ?', [event_id]);
        if (events.length === 0) {
            return res.status(404).json({ error: 'Event not found' });
        }
        
        const event = events[0];
        
        // VULNERABLE: User-controlled 'name' is directly interpolated into a Handlebars template
        // This enables Handlebars SSTI via prototype chain access
        const templateStr = `
            <div class="badge-preview">
                <div class="badge-header">EventBoard Badge</div>
                <div class="badge-content">
                    <div class="attendee-name">${name}</div>
                    <div class="event-name">${event.title}</div>
                    <div class="event-date">${event.event_date}</div>
                </div>
            </div>
        `;
        
        // Compile user-provided content directly into template
        // The context object provides access to prototype chain
        const template = Handlebars.compile(templateStr);
        
        // Create context with nested object that exposes prototype access
        const context = {
            config: {
                secret: FLAG,
                version: '1.2.3'
            }
        };
        
        const html = template(context);
        
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Badge Preview</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
                    .badge-preview { 
                        width: 300px; 
                        border: 2px solid #333; 
                        border-radius: 8px; 
                        padding: 20px; 
                        background: white;
                        margin: 20px auto;
                    }
                    .badge-header { 
                        text-align: center; 
                        font-weight: bold; 
                        font-size: 18px; 
                        border-bottom: 1px solid #ccc; 
                        padding-bottom: 10px; 
                        margin-bottom: 15px;
                    }
                    .attendee-name { 
                        font-size: 24px; 
                        font-weight: bold; 
                        text-align: center; 
                        color: #2c3e50;
                    }
                    .event-name { 
                        text-align: center; 
                        margin-top: 10px; 
                        color: #666;
                    }
                    .event-date { 
                        text-align: center; 
                        margin-top: 5px; 
                        font-size: 12px; 
                        color: #999;
                    }
                    .back-link { display: block; text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                ${html}
                <a href="/event/${event_id}" class="back-link">Back to Event</a>
            </body>
            </html>
        `);
    } catch (err) {
        console.error('Badge preview error:', err.message);
        res.status(500).json({ error: 'Template rendering failed', details: err.message });
    }
});

// Card template API - another vulnerable endpoint for SSTI
// This exposes template compilation directly with user input
app.get('/api/card', (req, res) => {
    const { template } = req.query;
    
    if (!template) {
        return res.json({ 
            usage: 'Provide a template parameter to generate cards',
            example: '/api/card?template={{name}}',
            available_fields: ['name', 'role', 'department']
        });
    }
    
    try {
        // VULNERABLE: Direct compilation of user-provided template string
        // CVE-2019-20920: Handlebars before 4.5.3 allows prototype access
        const compiled = Handlebars.compile(template);
        
        // Context with data that has prototype chain
        const contextData = {
            name: 'John Doe',
            role: 'Attendee',
            department: 'General'
        };
        
        // Store flag in a way accessible via prototype pollution
        contextData.__proto__.secretToken = FLAG;
        
        const result = compiled(contextData);
        res.json({ rendered: result });
    } catch (err) {
        res.status(400).json({ error: 'Template error', message: err.message });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', version: '1.2.3' });
});

// About page
app.get('/about', (req, res) => {
    res.render('about', { title: 'About EventBoard' });
});

// API endpoints
app.get('/api/events', async (req, res) => {
    try {
        const [events] = await db.query('SELECT id, title, event_date, location FROM events');
        res.json(events);
    } catch (err) {
        res.status(500).json({ error: 'Database error' });
    }
});

app.get('/api/stats', async (req, res) => {
    try {
        const [eventCount] = await db.query('SELECT COUNT(*) as count FROM events');
        const [feedbackCount] = await db.query('SELECT COUNT(*) as count FROM feedback');
        res.json({
            events: eventCount[0].count,
            feedback: feedbackCount[0].count,
            version: '1.2.3'
        });
    } catch (err) {
        res.status(500).json({ error: 'Database error' });
    }
});

// Start server
connectDB().then(() => {
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`EventBoard running on port ${PORT}`);
    });
});
