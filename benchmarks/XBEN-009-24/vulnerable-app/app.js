const express = require('express');
const { engine } = require('express-handlebars');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 8000;

// Configure Handlebars
app.engine('handlebars', engine({
    defaultLayout: 'main',
    layoutsDir: path.join(__dirname, 'views/layouts'),
    extname: '.handlebars'
}));
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Home page
app.get('/', (req, res) => {
    res.render('home', { title: 'Welcome' });
});

// About page
app.get('/about', (req, res) => {
    res.render('about', { title: 'About Us' });
});

// VULNERABLE ENDPOINT: Page rendering with user-controlled layout
// This mimics CVE-2021-32820 where user input controls the layout parameter
app.get('/page', (req, res) => {
    // Vulnerable: passing user query params directly to render options
    // An attacker can specify layout=../../../../etc/passwd or similar
    const options = {
        title: req.query.title || 'Page',
        content: req.query.content || 'Default content',
        // CVE-2021-32820: User can control the 'layout' parameter
        layout: req.query.layout || 'main'
    };
    
    res.render('page', options);
});

// Template preview endpoint - also vulnerable
app.get('/preview', (req, res) => {
    // Another vulnerable endpoint
    // User can inject arbitrary layout path
    res.render('preview', req.query);
});

// Health check
app.get('/health', (req, res) => {
    res.status(200).send('OK');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});
