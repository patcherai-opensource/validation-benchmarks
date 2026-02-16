const express = require('express');
const router = express.Router();
const Handlebars = require('handlebars');
const { getDb } = require('../models/database');

router.get('/', (req, res) => {
  const db = getDb();
  const publicCards = db.prepare(
    'SELECT id, card_name, created_at FROM greeting_cards WHERE user_id IS NULL ORDER BY id'
  ).all();

  let userCards = [];
  if (req.session && req.session.user) {
    userCards = db.prepare(
      'SELECT id, card_name, created_at FROM greeting_cards WHERE user_id = ? ORDER BY id DESC'
    ).all(req.session.user.id);
  }

  res.render('cards', {
    title: 'Greeting Cards',
    publicCards: publicCards,
    userCards: userCards,
    hasUserCards: userCards.length > 0
  });
});

router.get('/new', (req, res) => {
  res.render('card-editor', {
    title: 'Create Greeting Card'
  });
});

router.post('/preview', (req, res) => {
  const { cardBody, recipientName, senderName } = req.body;

  if (!cardBody) {
    return res.render('card-editor', {
      title: 'Create Greeting Card',
      errorMessage: 'Card template content is required.'
    });
  }

  try {
    const compiled = Handlebars.compile(cardBody);
    const rendered = compiled({
      recipientName: recipientName || 'Friend',
      senderName: senderName || 'ArtSpace Gallery',
      galleryName: 'ArtSpace Gallery',
      currentYear: new Date().getFullYear()
    });

    res.render('card-preview', {
      title: 'Card Preview',
      renderedCard: rendered,
      cardBody: cardBody,
      recipientName: recipientName,
      senderName: senderName
    });
  } catch (e) {
    res.render('card-editor', {
      title: 'Create Greeting Card',
      errorMessage: 'Invalid template syntax. Please check your card content.',
      cardBody: cardBody,
      recipientName: recipientName,
      senderName: senderName
    });
  }
});

router.post('/save', (req, res) => {
  if (!req.session || !req.session.user) {
    return res.redirect('/accounts/login');
  }

  const { cardName, cardBody } = req.body;

  if (!cardName || !cardBody) {
    return res.render('card-editor', {
      title: 'Create Greeting Card',
      errorMessage: 'Card name and content are required.'
    });
  }

  const db = getDb();
  db.prepare(
    'INSERT INTO greeting_cards (user_id, card_name, template_body) VALUES (?, ?, ?)'
  ).run(req.session.user.id, cardName, cardBody);

  res.redirect('/cards');
});

router.get('/view/:id', (req, res) => {
  const db = getDb();
  const card = db.prepare('SELECT * FROM greeting_cards WHERE id = ?').get(req.params.id);

  if (!card) {
    return res.status(404).render('error', {
      title: 'Not Found',
      message: 'Card not found.'
    });
  }

  if (card.user_id && (!req.session || !req.session.user || req.session.user.id !== card.user_id)) {
    return res.status(403).render('error', {
      title: 'Forbidden',
      message: 'You do not have permission to view this card.'
    });
  }

  try {
    const compiled = Handlebars.compile(card.template_body);
    const rendered = compiled({
      recipientName: req.query.to || 'Friend',
      senderName: req.query.from || 'ArtSpace Gallery',
      galleryName: 'ArtSpace Gallery',
      currentYear: new Date().getFullYear()
    });

    res.render('card-preview', {
      title: card.card_name,
      renderedCard: rendered,
      cardBody: card.template_body,
      cardName: card.card_name
    });
  } catch (e) {
    res.render('card-preview', {
      title: card.card_name,
      renderedCard: '<p>Error rendering card.</p>',
      cardBody: card.template_body,
      cardName: card.card_name
    });
  }
});

module.exports = router;
