const express = require('express');
const exphbs = require('express-handlebars');
const path = require('path');
const session = require('express-session');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');

const galleryRoutes = require('./routes/gallery');
const accountRoutes = require('./routes/accounts');
const exhibitionRoutes = require('./routes/exhibitions');
const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 80;

// View engine setup
var hbs = exphbs.create({
    defaultLayout: 'main',
    layoutsDir: path.join(__dirname, 'views/layouts'),
    partialsDir: path.join(__dirname, 'views/partials'),
    helpers: {
        formatPrice: function(price) {
            return parseFloat(price).toFixed(2);
        },
        eq: function(a, b) {
            return a === b;
        },
        currentYear: function() {
            return new Date().getFullYear();
        },
        truncate: function(str, len) {
            if (str && str.length > len) {
                return str.substring(0, len) + '...';
            }
            return str;
        }
    }
});
app.engine('handlebars', hbs.engine);
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));

// Security and middleware
app.use(helmet({
    contentSecurityPolicy: false,
    crossOriginEmbedderPolicy: false
}));
app.use(compression());
app.use(morgan('combined'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
    secret: 'arthaus-session-key-x7k9m2p4',
    resave: false,
    saveUninitialized: false,
    cookie: {
        maxAge: 3600000,
        httpOnly: true
    }
}));

// Static files
app.use('/static', express.static(path.join(__dirname, 'public')));

// Make session data available to templates
app.use(function(req, res, next) {
    res.locals.user = req.session.user || null;
    res.locals.isAuthenticated = !!req.session.user;
    next();
});

// Routes
app.use('/', galleryRoutes);
app.use('/accounts', accountRoutes);
app.use('/exhibitions', exhibitionRoutes);
app.use('/api', apiRoutes);

// 404 handler
app.use(function(req, res) {
    res.status(404).render('pages/error', {
        title: 'Page Not Found',
        message: 'The page you are looking for does not exist.',
        statusCode: 404
    });
});

// Error handler
app.use(function(err, req, res, next) {
    res.status(500).render('pages/error', {
        title: 'Internal Server Error',
        message: 'Something went wrong. Please try again later.',
        statusCode: 500
    });
});

app.listen(PORT, '0.0.0.0', function() {
    console.log('ArtHaus Gallery running on port ' + PORT);
});
