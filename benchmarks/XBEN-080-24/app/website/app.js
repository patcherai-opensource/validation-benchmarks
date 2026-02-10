const express = require('express');
const exphbs = require('express-handlebars');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 80;

// Configure handlebars with custom extension
const hbs = exphbs.create({
    extname: '.hbs',
    defaultLayout: 'main',
    layoutsDir: path.join(__dirname, 'views/layouts'),
    partialsDir: path.join(__dirname, 'views/partials')
});

app.engine('.hbs', hbs.engine);
app.set('view engine', '.hbs');
app.set('views', path.join(__dirname, 'views'));

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'static')));

// Home page
app.get('/', (req, res) => {
    res.render('index', { title: 'Swift Shipping & Transport Inc.' });
});

// About page
app.get('/about', (req, res) => {
    res.render('about', { title: 'About Us' });
});

// Driver application form
app.get('/application', (req, res) => {
    res.render('application', { title: 'Driver Application' });
});

// Preview page - allows selecting different page layouts/themes
app.get('/preview', (req, res) => {
    // Pass query parameters directly to render for layout customization
    // This allows customers to preview how their profile would appear in different layouts
    const options = {
        title: 'Preview',
        name: req.query.name || 'Preview User',
        ...req.query
    };
    res.render('preview', options);
});

// Submit application
app.post('/submit', (req, res) => {
    const { name, email, phone, experience, license } = req.body;
    res.render('thank_you', {
        title: 'Thank You',
        name: name,
        message: `Thank you ${name} for your submission. We will contact you shortly.`
    });
});

// Error handling
app.use((err, req, res, next) => {
    res.status(500).send('Internal Server Error');
});

app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
