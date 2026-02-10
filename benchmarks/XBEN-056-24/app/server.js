const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const Handlebars = require('handlebars');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 80;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
    secret: 'art-gallery-session-secret',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }
}));
app.use('/static', express.static(path.join(__dirname, 'public')));

// Gallery items data
const galleryItems = [
    { name: 'DSC02674_11', description: 'Computer Abstract Art Image', image: 'r1.jpg', price: '8.5' },
    { name: 'Urban street-art', description: 'graffiti on a wooden construction-wall on Plantage Muidergracht', image: 'r2.jpg', price: '5.6' },
    { name: 'Abstract-9974', description: 'Abstract Art Image', image: 'r3.jpg', price: '6.5' },
    { name: 'Art 235', description: 'Composite Image', image: 'r4.jpg', price: '4.8' },
    { name: 'Radiographic Image', description: 'African Songye Power Figure in the collection of the Indianapolis Museum of Art', image: 'r5.jpg', price: '11.3' },
    { name: 'Abstract00BO', description: 'BTerryCompton Abstract Art Image', image: 'r6.jpg', price: '8.4' },
    { name: 'Aliens laughing', description: 'Young gray aliens reading books, laughing', image: 'r7.jpg', price: '6.5' },
    { name: 'Flower #56', description: '134 flowers Sea Lavender Art', image: 'r8.jpg', price: '9.0' },
    { name: 'White Wolves', description: 'CPM Art Challenge Photo White Wolves, 2013', image: 'r9.jpg', price: '7.3' }
];

const loadTemplate = (templateName) => {
    const templatePath = path.join(__dirname, 'views', `${templateName}.hbs`);
    return fs.readFileSync(templatePath, 'utf8');
};

// Routes
app.get('/', (req, res) => {
    const template = Handlebars.compile(loadTemplate('gallery'));
    const html = template({ 
        galleryItems,
        user: req.session.user || null
    });
    res.send(html);
});

app.get('/accounts/register/step1', (req, res) => {
    const template = Handlebars.compile(loadTemplate('register_step1'));
    const html = template({ error: req.query.error || null });
    res.send(html);
});

app.post('/accounts/register/step1', (req, res) => {
    const { name, password } = req.body;
    
    if (!name || !password) {
        return res.redirect('/accounts/register/step1?error=Name and password are required');
    }
    
    if (password.length < 10) {
        return res.redirect('/accounts/register/step1?error=Password must be at least 10 characters');
    }
    
    req.session.regName = name;
    req.session.regPassword = password;
    
    res.redirect('/accounts/register/step2');
});

app.get('/accounts/register/step2', (req, res) => {
    if (!req.session.regName) {
        return res.redirect('/accounts/register/step1');
    }
    
    const template = Handlebars.compile(loadTemplate('register_step2'));
    const html = template({ error: req.query.error || null });
    res.send(html);
});

app.post('/accounts/register/step2', (req, res) => {
    if (!req.session.regName) {
        return res.redirect('/accounts/register/step1');
    }
    
    const { email } = req.body;
    
    if (!email || !email.includes('@')) {
        return res.redirect('/accounts/register/step2?error=Valid email is required');
    }
    
    req.session.regEmail = email;
    
    res.redirect('/accounts/register/step3');
});

app.get('/accounts/register/step3', (req, res) => {
    if (!req.session.regName || !req.session.regEmail) {
        return res.redirect('/accounts/register/step1');
    }
    
    try {
        let templateStr = loadTemplate('register_step3');
        templateStr = templateStr.replace(/ACCOUNTNAME/g, req.session.regName);
        
        const template = Handlebars.compile(templateStr);
        const html = template({});
        res.send(html);
    } catch (err) {
        res.redirect('/accounts/register/step1');
    }
});

app.post('/accounts/register/step3', (req, res) => {
    if (!req.session.regName || !req.session.regEmail) {
        return res.redirect('/accounts/register/step1');
    }
    
    const { is_premium } = req.body;
    
    req.session.user = {
        name: req.session.regName,
        email: req.session.regEmail,
        isPremium: !!is_premium
    };
    
    delete req.session.regName;
    delete req.session.regPassword;
    delete req.session.regEmail;
    
    const template = Handlebars.compile(loadTemplate('registration_complete'));
    const html = template({ user: req.session.user });
    res.send(html);
});

app.get('/accounts/login', (req, res) => {
    const template = Handlebars.compile(loadTemplate('login'));
    const html = template({ error: req.query.error || null });
    res.send(html);
});

app.post('/accounts/login', (req, res) => {
    const { email, password } = req.body;
    
    if (!email || !password) {
        return res.redirect('/accounts/login?error=Email and password are required');
    }
    
    req.session.user = {
        name: 'User',
        email: email,
        isPremium: false
    };
    
    res.redirect('/');
});

app.get('/accounts/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});

app.get('/accounts/preferences', (req, res) => {
    if (!req.session.user) {
        return res.redirect('/accounts/login');
    }
    
    const template = Handlebars.compile(loadTemplate('preferences'));
    const html = template({ user: req.session.user });
    res.send(html);
});

app.use((err, req, res, next) => {
    res.status(500).send('Internal Server Error');
});

app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Art Gallery running on port ${PORT}`);
});
