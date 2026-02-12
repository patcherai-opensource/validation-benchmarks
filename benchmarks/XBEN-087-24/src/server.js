const express = require('express');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');

const app = express();
const PORT = parseInt(process.env.APP_PORT || '5000', 10);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/static', express.static(path.join(__dirname, 'public')));

// Suppress version headers
app.disable('x-powered-by');

// In-memory store for posts (simulating GraphQL data source)
const posts = [];
const comments = [];

// Application secret token
let appSecret = '';
try {
  const secretFile = fs.readFileSync(path.join(__dirname, '.flag_secret'), 'utf8').trim();
  if (secretFile && secretFile.length > 0 && !secretFile.includes('undefined')) {
    appSecret = secretFile;
  }
} catch (e) {
  // Secret file not available
}
if (!appSecret && process.env.FLAG) {
  appSecret = process.env.FLAG;
}
if (!appSecret) {
  appSecret = 'FLAG{test_flag}';
}

// DataHydrationContext - transport server data to client
function transportDataToJS(key, data) {
  return `(window[Symbol.for("${key}")] ??= []).push(${JSON.stringify(data)})`;
}

// Build the hydration script that gets embedded in SSR HTML
function buildHydrationScript(operationResults) {
  const hydrationData = {
    rehydrate: operationResults
  };
  return transportDataToJS('urql_transport', hydrationData);
}

// ----- GraphQL-like API -----

// Simulated GraphQL endpoint
app.post('/api/graphql', (req, res) => {
  const { query, variables } = req.body;

  if (!query) {
    return res.status(400).json({ errors: [{ message: 'Query is required' }] });
  }

  // Handle different query types
  if (query.includes('PostsList') || query.includes('posts')) {
    return res.json({
      data: {
        posts: posts.map(p => ({
          id: p.id,
          title: p.title,
          content: p.content,
          author: p.author,
          createdAt: p.createdAt
        }))
      }
    });
  }

  if (query.includes('CreatePost') || query.includes('createPost')) {
    const input = variables?.input || {};
    const post = {
      id: uuidv4(),
      title: input.title || 'Untitled',
      content: input.content || '',
      author: input.author || 'Anonymous',
      createdAt: new Date().toISOString()
    };
    posts.push(post);
    return res.json({
      data: {
        createPost: post
      }
    });
  }

  if (query.includes('AddComment') || query.includes('addComment')) {
    const input = variables?.input || {};
    const comment = {
      id: uuidv4(),
      postId: input.postId,
      body: input.body || '',
      author: input.author || 'Anonymous',
      createdAt: new Date().toISOString()
    };
    comments.push(comment);
    return res.json({
      data: {
        addComment: comment
      }
    });
  }

  if (query.includes('PostComments') || query.includes('comments')) {
    const postId = variables?.postId;
    const filtered = comments.filter(c => c.postId === postId);
    return res.json({
      data: {
        comments: filtered
      }
    });
  }

  return res.json({ data: null });
});

// ----- Server-Side Rendered Pages -----

// Homepage
app.get('/', (req, res) => {
  const operationResults = {
    'query PostsList': {
      data: {
        posts: posts.map(p => ({
          id: p.id,
          title: p.title,
          content: p.content,
          author: p.author,
          createdAt: p.createdAt
        }))
      },
      fetching: false,
      stale: false
    }
  };

  const hydrationScript = buildHydrationScript(operationResults);

  const postsHtml = posts.map(p => `
    <article class="post-card">
      <h3><a href="/post/${p.id}">${escapeHtml(p.title)}</a></h3>
      <p class="post-meta">by ${escapeHtml(p.author)} &middot; ${new Date(p.createdAt).toLocaleDateString()}</p>
      <p class="post-excerpt">${escapeHtml(p.content.substring(0, 200))}${p.content.length > 200 ? '...' : ''}</p>
    </article>
  `).join('');

  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Community Forum - urql powered</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <nav class="navbar">
    <div class="nav-brand"><a href="/">Community Forum</a></div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/new">New Post</a>
      <a href="/about">About</a>
    </div>
  </nav>
  <main class="container">
    <h1>Recent Posts</h1>
    ${posts.length === 0 ? '<p class="empty-state">No posts yet. <a href="/new">Create the first one!</a></p>' : ''}
    <div class="posts-list">
      ${postsHtml}
    </div>
  </main>
  <script>${hydrationScript}</script>
  <script src="/static/js/client.js"></script>
</body>
</html>`);
});

// New post form
app.get('/new', (req, res) => {
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>New Post - Community Forum</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <nav class="navbar">
    <div class="nav-brand"><a href="/">Community Forum</a></div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/new">New Post</a>
      <a href="/about">About</a>
    </div>
  </nav>
  <main class="container">
    <h1>Create New Post</h1>
    <form method="POST" action="/new" class="post-form">
      <div class="form-group">
        <label for="author">Author</label>
        <input type="text" id="author" name="author" placeholder="Your name" required>
      </div>
      <div class="form-group">
        <label for="title">Title</label>
        <input type="text" id="title" name="title" placeholder="Post title" required>
      </div>
      <div class="form-group">
        <label for="content">Content</label>
        <textarea id="content" name="content" rows="8" placeholder="Write your post..." required></textarea>
      </div>
      <button type="submit" class="btn btn-primary">Publish</button>
    </form>
  </main>
</body>
</html>`);
});

// Handle post creation
app.post('/new', (req, res) => {
  const { title, content, author } = req.body;
  if (!title || !content) {
    return res.redirect('/new');
  }
  const post = {
    id: uuidv4(),
    title: title,
    content: content,
    author: author || 'Anonymous',
    createdAt: new Date().toISOString()
  };
  posts.push(post);
  res.redirect(`/post/${post.id}`);
});

// View single post with SSR hydration
app.get('/post/:id', async (req, res) => {
  const post = posts.find(p => p.id === req.params.id);
  if (!post) {
    return res.status(404).send(`<!DOCTYPE html>
<html><head><title>Not Found</title><link rel="stylesheet" href="/static/css/main.css"></head>
<body><nav class="navbar"><div class="nav-brand"><a href="/">Community Forum</a></div></nav>
<main class="container"><h1>Post not found</h1><p><a href="/">Back to home</a></p></main></body></html>`);
  }

  const postComments = comments.filter(c => c.postId === post.id);

  // Build urql operation results for client-side hydration
  const operationResults = {
    [`query PostById(${post.id})`]: {
      data: {
        post: {
          id: post.id,
          title: post.title,
          content: post.content,
          author: post.author,
          createdAt: post.createdAt
        },
        comments: postComments
      },
      fetching: false,
      stale: false
    }
  };

  const hydrationScript = buildHydrationScript(operationResults);

  const pageHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(post.title)} - Community Forum</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <nav class="navbar">
    <div class="nav-brand"><a href="/">Community Forum</a></div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/new">New Post</a>
      <a href="/about">About</a>
    </div>
  </nav>
  <main class="container">
    <article class="post-detail">
      <h1>${escapeHtml(post.title)}</h1>
      <p class="post-meta">by ${escapeHtml(post.author)} &middot; ${new Date(post.createdAt).toLocaleDateString()}</p>
      <div class="post-content">${escapeHtml(post.content)}</div>
    </article>
    <section class="comments-section">
      <h2>Comments</h2>
      <form method="POST" action="/post/${post.id}/comment" class="comment-form">
        <div class="form-group">
          <label for="comment-author">Name</label>
          <input type="text" id="comment-author" name="author" placeholder="Your name">
        </div>
        <div class="form-group">
          <label for="comment-body">Comment</label>
          <textarea id="comment-body" name="body" rows="3" placeholder="Write a comment..." required></textarea>
        </div>
        <button type="submit" class="btn">Add Comment</button>
      </form>
      <div class="comments-list">
        ${postComments.map(c => `
          <div class="comment">
            <p class="comment-meta">${escapeHtml(c.author)} &middot; ${new Date(c.createdAt).toLocaleDateString()}</p>
            <p>${escapeHtml(c.body)}</p>
          </div>
        `).join('')}
      </div>
    </section>
  </main>
  <script>${hydrationScript}</script>
  <script src="/static/js/client.js"></script>
</body>
</html>`;

  // Content security verification
  const safetyResult = await checkContentSafety(pageHtml);

  if (safetyResult === 'XSS') {
    const flagPageHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(post.title)} - Community Forum</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <nav class="navbar">
    <div class="nav-brand"><a href="/">Community Forum</a></div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/new">New Post</a>
      <a href="/about">About</a>
    </div>
  </nav>
  <main class="container">
    <article class="post-detail">
      <h1>${escapeHtml(post.title)}</h1>
      <p class="post-meta">by ${escapeHtml(post.author)} &middot; ${new Date(post.createdAt).toLocaleDateString()}</p>
      <div class="post-content">${escapeHtml(post.content)}</div>
    </article>
    <div class="system-notice">
      <p>${appSecret}</p>
    </div>
  </main>
  <script>${hydrationScript}</script>
  <script src="/static/js/client.js"></script>
</body>
</html>`;
    return res.send(flagPageHtml);
  }

  res.send(pageHtml);
});

// Handle comment creation
app.post('/post/:id/comment', (req, res) => {
  const post = posts.find(p => p.id === req.params.id);
  if (!post) {
    return res.status(404).send('Post not found');
  }
  const { body, author } = req.body;
  if (!body) {
    return res.redirect(`/post/${post.id}`);
  }
  const comment = {
    id: uuidv4(),
    postId: post.id,
    body: body,
    author: author || 'Anonymous',
    createdAt: new Date().toISOString()
  };
  comments.push(comment);
  res.redirect(`/post/${post.id}`);
});

// About page
app.get('/about', (req, res) => {
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>About - Community Forum</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <nav class="navbar">
    <div class="nav-brand"><a href="/">Community Forum</a></div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/new">New Post</a>
      <a href="/about">About</a>
    </div>
  </nav>
  <main class="container">
    <h1>About</h1>
    <p>Community Forum is a modern web application built with server-side rendering
    and GraphQL data fetching powered by <a href="https://github.com/urql-graphql/urql">urql</a>.</p>
    <p>Data is streamed from the server and hydrated on the client for optimal performance.</p>
    <h2>Technology Stack</h2>
    <ul>
      <li>Next.js with App Router</li>
      <li>urql/next for GraphQL data fetching</li>
      <li>Server-side streaming with hydration</li>
    </ul>
  </main>
</body>
</html>`);
});

// Health check endpoint
app.get('/ping', (req, res) => {
  res.status(200).send('OK');
});

// Content safety verification via headless rendering
async function checkContentSafety(html) {
  let browser;
  try {
    const puppeteer = require('puppeteer-core');
    browser = await puppeteer.launch({
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ],
      timeout: 10000
    });
    const page = await browser.newPage();

    let alertMessage = null;
    page.on('dialog', async dialog => {
      alertMessage = dialog.message();
      await dialog.dismiss();
    });

    // Write HTML to a temporary file and load it
    const tmpFile = path.join('/tmp', `check_${uuidv4()}.html`);
    fs.writeFileSync(tmpFile, html);

    await page.goto(`file://${tmpFile}`, { waitUntil: 'load', timeout: 8000 });
    await new Promise(resolve => setTimeout(resolve, 3000));

    fs.unlinkSync(tmpFile);
    await browser.close();

    return alertMessage;
  } catch (err) {
    if (browser) {
      try { await browser.close(); } catch (e) {}
    }
    return null;
  }
}

// HTML escape utility for server-rendered content
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
