const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const path = require('path');
const helmet = require('helmet');
const exphbs = require('express-handlebars');

const galleryRoutes = require('./routes/gallery');
const accountRoutes = require('./routes/accounts');
const cardRoutes = require('./routes/cards');
const db = require('./models/database');

const app = express();
const PORT = process.env.PORT || 80;

const hbs = exphbs.create({
  defaultLayout: 'main',
  layoutsDir: path.join(__dirname, 'views/layouts'),
  partialsDir: path.join(__dirname, 'views/partials'),
  extname: '.handlebars'
});

app.engine('handlebars', hbs.engine);
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));

app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
  secret: 'k8j3m9x2v7q1w5z0',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 3600000 }
}));

app.use(express.static(path.join(__dirname, 'public')));

app.use((req, res, next) => {
  res.locals.user = req.session.user || null;
  res.locals.isAuthenticated = !!req.session.user;
  next();
});

app.use('/', galleryRoutes);
app.use('/accounts', accountRoutes);
app.use('/cards', cardRoutes);

app.use((req, res) => {
  res.status(404).render('error', { 
    title: 'Not Found',
    message: 'The page you are looking for does not exist.'
  });
});

app.use((err, req, res, next) => {
  res.status(500).render('error', {
    title: 'Server Error',
    message: 'An unexpected error occurred.'
  });
});

db.initialize();

app.listen(PORT, '0.0.0.0', () => {
  console.log(`ArtSpace Gallery running on port ${PORT}`);
});
