'use strict';

const express = require('express');
const router = express.Router();

function renderMarkdown(text) {
  if (!text) return '';
  let html = text;
  // Escape HTML
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  // Handle escaped newlines from database
  html = html.replace(/\\n/g, '\n');
  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // Bold and italic
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
  // Unordered list items
  html = html.replace(/^- \[x\] (.+)$/gm, '<li class="done">☑ $1</li>');
  html = html.replace(/^- \[ \] (.+)$/gm, '<li class="todo">☐ $1</li>');
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  // Ordered list items
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
  // Horizontal rule
  html = html.replace(/^---$/gm, '<hr>');
  // Table (simple)
  html = html.replace(/^\|(.+)\|$/gm, function(match, content) {
    const cells = content.split('|').map(function(c) { return c.trim(); });
    if (cells.every(function(c) { return /^[-:]+$/.test(c); })) return '';
    return '<tr>' + cells.map(function(c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
  });
  // Code blocks
  html = html.replace(/```[\s\S]*?```/g, function(match) {
    return '<pre><code>' + match.replace(/```\w*\n?/g, '').replace(/```/g, '') + '</code></pre>';
  });
  // Paragraphs (double newline)
  html = html.replace(/\n\n/g, '</p><p>');
  // Single newlines to line breaks
  html = html.replace(/\n/g, '<br>');
  html = '<p>' + html + '</p>';
  return html;
}

// Render wiki page
router.get('*', (req, res) => {
  const db = req.app.get('db');
  const pagePath = req.path === '/' ? '/' : req.path.replace(/\/$/, '');

  const page = db.prepare('SELECT p.*, u.name as creatorName FROM pages p LEFT JOIN users u ON p.creator = u.id WHERE p.path = ?').get(pagePath);

  if (!page) {
    const childPages = db.prepare('SELECT path, title, updatedAt FROM pages WHERE path LIKE ? AND path != ? ORDER BY path').all(pagePath + '/%', pagePath);

    if (childPages.length > 0) {
      return res.render('page-list', {
        title: pagePath + ' - GROWI',
        currentPath: pagePath,
        pages: childPages,
        user: req.user || null
      });
    }

    return res.status(404).render('not-found', {
      title: 'Page Not Found - GROWI',
      path: pagePath,
      user: req.user || null
    });
  }

  const comments = db.prepare('SELECT c.*, u.name as authorName FROM comments c LEFT JOIN users u ON c.creator = u.id WHERE c.pageId = ? ORDER BY c.createdAt DESC').all(page.id);

  res.render('page', {
    title: page.title + ' - GROWI',
    page: page,
    comments: comments,
    user: req.user || null,
    currentPath: pagePath,
    renderMarkdown: renderMarkdown
  });
});

module.exports = router;
