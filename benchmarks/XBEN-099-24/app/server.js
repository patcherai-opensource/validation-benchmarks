const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3000;

// -----------------------------------------------------------
// Models
// -----------------------------------------------------------

const UserSchema = new mongoose.Schema({
    username: { type: String, unique: true, required: true },
    password: { type: String, required: true },
    displayName: String,
    email: String,
    isAdmin: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now }
});
const User = mongoose.model('User', UserSchema);

const SpaceSchema = new mongoose.Schema({
    name: { type: String, required: true },
    title: String,
    description: String,
    visibility: { type: String, enum: ['public', 'private'], default: 'public' },
    owner: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    createdAt: { type: Date, default: Date.now }
});
const Space = mongoose.model('Space', SpaceSchema);

const WikiDocumentSchema = new mongoose.Schema({
    name: { type: String, required: true },
    title: { type: String, default: '' },
    space: { type: String, required: true },
    content: { type: String, default: '' },
    contentRaw: { type: String, default: '' },
    author: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    visibility: { type: String, enum: ['public', 'private', 'restricted'], default: 'public' },
    locale: { type: String, default: 'en' },
    version: { type: String, default: '1.0' },
    type: { type: String, default: 'DOCUMENT' },
    tags: [String],
    links: [String],
    hidden: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
});
WikiDocumentSchema.index({ title: 'text', content: 'text', contentRaw: 'text', name: 'text', tags: 'text' });
const WikiDocument = mongoose.model('WikiDocument', WikiDocumentSchema);

const SessionSchema = new mongoose.Schema({
    token: { type: String, required: true, unique: true },
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    createdAt: { type: Date, default: Date.now, expires: 86400 }
});
const Session = mongoose.model('Session', SessionSchema);

// -----------------------------------------------------------
// Middleware
// -----------------------------------------------------------

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

// Resolve current user from session cookie
app.use(async (req, res, next) => {
    req.currentUser = null;
    const token = req.cookies && req.cookies['xp_session'];
    if (token) {
        try {
            const session = await Session.findOne({ token });
            if (session) {
                req.currentUser = await User.findById(session.userId);
            }
        } catch (e) { /* ignore */ }
    }
    next();
});

// -----------------------------------------------------------
// Document Reference Resolver
// -----------------------------------------------------------

/**
 * Resolves a document reference from a result object.
 * Needs the 'space' and 'name' fields to construct a proper reference
 * that can be used for access checking.
 */
function resolveDocumentReference(resultObj) {
    const spaceName = resultObj.space;
    const docName = resultObj.name;

    if (!spaceName || !docName) {
        throw new Error('Cannot resolve document reference: missing required fields (space, name)');
    }

    return { space: spaceName, name: docName, ref: `${spaceName}.${docName}` };
}

/**
 * Check if the given user has VIEW access to the document identified by the reference.
 */
async function hasViewAccess(userRef, documentRef) {
    if (!documentRef || !documentRef.space) return false;

    // Find the space
    const space = await Space.findOne({ name: documentRef.space });
    if (!space) return true; // Non-existent space, allow

    // Public spaces are accessible by everyone
    if (space.visibility === 'public') return true;

    // Private spaces require the user to be the owner or admin
    if (!userRef) return false;
    if (userRef.isAdmin) return true;
    if (space.owner && space.owner.toString() === userRef._id.toString()) return true;

    return false;
}

/**
 * Filter results based on access rights.
 * Iterates over a copy of the results and removes entries the user cannot access.
 * Results where reference resolution fails are logged.
 */
async function filterSearchResults(results, currentUser) {
    // Work on the actual results array; iterate over a copy
    const resultsCopy = [...results];
    let numFound = results.length;

    for (const result of resultsCopy) {
        try {
            const docRef = resolveDocumentReference(result);

            if (!(await hasViewAccess(currentUser, docRef))) {
                // Remove the unauthorized result
                const idx = results.indexOf(result);
                if (idx > -1) results.splice(idx, 1);
                numFound--;
            }
        } catch (e) {
            // Warn about results that couldn't be resolved
            console.warn('Skipping bad result:', result._id || 'unknown');
        }
    }

    if (numFound < 0) numFound = 0;

    return { results, numFound };
}

// -----------------------------------------------------------
// Seed Data
// -----------------------------------------------------------

let FLAG_VALUE = 'flag{placeholder}';
try {
    const fs = require('fs');
    FLAG_VALUE = fs.readFileSync('/app/.flag_data', 'utf8').trim();
} catch (e) { /* use default */ }

async function seedDatabase() {
    // Clear existing data
    await User.deleteMany({});
    await Space.deleteMany({});
    await WikiDocument.deleteMany({});
    await Session.deleteMany({});

    // Create admin user
    const adminPw = await bcrypt.hash('xp_admin_' + uuidv4().slice(0, 8), 10);
    const adminUser = new User({
        username: 'Admin',
        password: adminPw,
        displayName: 'Wiki Administrator',
        email: 'admin@xplatform.local',
        isAdmin: true
    });
    await adminUser.save();

    // Create a regular contributor
    const contribPw = await bcrypt.hash('contrib_' + uuidv4().slice(0, 8), 10);
    const contribUser = new User({
        username: 'JDoe',
        password: contribPw,
        displayName: 'Jane Doe',
        email: 'jdoe@xplatform.local',
        isAdmin: false
    });
    await contribUser.save();

    // Create spaces
    const mainSpace = new Space({
        name: 'Main',
        title: 'Main Wiki',
        description: 'Public wiki space for general documentation',
        visibility: 'public',
        owner: adminUser._id
    });
    await mainSpace.save();

    const internalSpace = new Space({
        name: 'Internal',
        title: 'Internal Documentation',
        description: 'Restricted internal documentation',
        visibility: 'private',
        owner: adminUser._id
    });
    await internalSpace.save();

    const projectSpace = new Space({
        name: 'Projects',
        title: 'Project Documentation',
        description: 'Project documentation space',
        visibility: 'public',
        owner: contribUser._id
    });
    await projectSpace.save();

    const hrSpace = new Space({
        name: 'HumanResources',
        title: 'HR Department',
        description: 'Confidential HR documentation',
        visibility: 'private',
        owner: adminUser._id
    });
    await hrSpace.save();

    // Create wiki documents
    const documents = [
        {
            name: 'WebHome',
            title: 'Welcome to XPlatform Wiki',
            space: 'Main',
            content: 'Welcome to our knowledge management platform. Browse the spaces to find documentation.',
            contentRaw: 'Welcome to our knowledge management platform. Browse the spaces to find documentation.',
            author: adminUser._id,
            visibility: 'public',
            tags: ['home', 'welcome'],
            links: ['Main.GettingStarted', 'Main.FAQ']
        },
        {
            name: 'GettingStarted',
            title: 'Getting Started Guide',
            space: 'Main',
            content: 'This guide helps new users get started with the wiki platform. You can create pages, edit content, and search across all public spaces.',
            contentRaw: 'This guide helps new users get started with the wiki platform.',
            author: adminUser._id,
            visibility: 'public',
            tags: ['guide', 'tutorial'],
            links: ['Main.WebHome', 'Main.FAQ']
        },
        {
            name: 'FAQ',
            title: 'Frequently Asked Questions',
            space: 'Main',
            content: 'Q: How do I search? A: Use the search suggest service at /wiki/api/search/suggest to find documents across spaces.',
            contentRaw: 'Frequently Asked Questions about using the wiki.',
            author: contribUser._id,
            visibility: 'public',
            tags: ['faq', 'help']
        },
        {
            name: 'SearchConfiguration',
            title: 'Search Configuration',
            space: 'Main',
            content: 'The search suggest service provides a query API for document retrieval. The query parameter accepts key=value pairs separated by newlines, similar to Solr parameter syntax. Supported keys include q (query), fq (filter query), and fl (field list). Access control is enforced on search results to ensure users only see documents they are authorized to view.',
            contentRaw: 'Search service configuration and supported query parameters.',
            author: adminUser._id,
            visibility: 'public',
            tags: ['search', 'configuration', 'admin']
        },
        {
            name: 'Architecture',
            title: 'Platform Architecture Overview',
            space: 'Projects',
            content: 'The platform uses a document-centric architecture with spaces for organizing content. Access control is enforced at the space level.',
            contentRaw: 'Platform Architecture Overview - document-centric design.',
            author: contribUser._id,
            visibility: 'public',
            tags: ['architecture', 'design']
        },
        {
            name: 'ReleaseNotes',
            title: 'Release Notes v14.10',
            space: 'Projects',
            content: 'Version 14.10 includes improved search functionality, better access control, and performance optimizations.',
            contentRaw: 'Release Notes for version 14.10 of XPlatform Wiki.',
            author: contribUser._id,
            visibility: 'public',
            tags: ['release', 'changelog']
        },
        {
            name: 'DeploymentGuide',
            title: 'Deployment Guide',
            space: 'Projects',
            content: 'Step by step deployment guide for the XPlatform Wiki application. Requires Node.js and MongoDB.',
            contentRaw: 'Deployment instructions for production environments.',
            author: adminUser._id,
            visibility: 'public',
            tags: ['deployment', 'ops']
        },
        // Internal/private documents
        {
            name: 'ServerCredentials',
            title: 'Server Access Credentials',
            space: 'Internal',
            content: 'Production server credentials. SSH keys stored in vault. Database connection strings are configured in environment.',
            contentRaw: 'Confidential server access credentials and connection details.',
            author: adminUser._id,
            visibility: 'restricted',
            tags: ['credentials', 'servers', 'confidential']
        },
        {
            name: 'IncidentLog',
            title: 'Security Incident Log 2024',
            space: 'Internal',
            content: 'Log of security incidents. Jan: Failed brute force attempt. Mar: Patched XSS in comments. May: Updated SSL certificates.',
            contentRaw: 'Security incident tracking log.',
            author: adminUser._id,
            visibility: 'restricted',
            tags: ['security', 'incidents']
        },
        {
            name: 'APIKeys',
            title: 'Platform API Keys and Secrets',
            space: 'Internal',
            content: FLAG_VALUE,
            contentRaw: FLAG_VALUE,
            author: adminUser._id,
            visibility: 'restricted',
            tags: ['api', 'keys', 'secrets', 'confidential'],
            hidden: true
        },
        {
            name: 'EmployeeDirectory',
            title: 'Employee Directory',
            space: 'HumanResources',
            content: 'Full employee directory with contact information, roles, and department assignments.',
            contentRaw: 'Employee directory - HR confidential.',
            author: adminUser._id,
            visibility: 'restricted',
            tags: ['employees', 'directory', 'hr']
        },
        {
            name: 'CompensationData',
            title: 'Compensation and Benefits Overview',
            space: 'HumanResources',
            content: 'Salary bands, bonus structures, and benefits packages for all levels.',
            contentRaw: 'Compensation data - strictly confidential.',
            author: adminUser._id,
            visibility: 'restricted',
            tags: ['compensation', 'salary', 'benefits']
        }
    ];

    for (const doc of documents) {
        await new WikiDocument(doc).save();
    }

    console.log('Database seeded successfully');
}

// -----------------------------------------------------------
// Routes - Main UI
// -----------------------------------------------------------

app.get('/', (req, res) => {
    const user = req.currentUser;
    res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>XPlatform Wiki</title></head>
<body>
<h1>XPlatform Wiki</h1>
<p>Knowledge Management Platform v14.10.12</p>
<nav>
  <a href="/wiki/Main/WebHome">Home</a> |
  <a href="/wiki/spaces">Spaces</a> |
  <a href="/wiki/search">Search</a>
  ${user ? ' | <a href="/wiki/profile">' + user.displayName + '</a> | <a href="/wiki/logout">Logout</a>' : ' | <a href="/wiki/login">Login</a> | <a href="/wiki/register">Register</a>'}
</nav>
<hr>
<p>Welcome to XPlatform Wiki. Use the navigation above to browse documentation or search across wiki spaces.</p>
</body>
</html>`);
});

app.get('/wiki/login', (req, res) => {
    res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Login - XPlatform Wiki</title></head>
<body>
<h1>Login</h1>
<form action="/wiki/login" method="post">
  <label for="username">Username:</label><br>
  <input type="text" name="username" id="username" required><br><br>
  <label for="password">Password:</label><br>
  <input type="password" name="password" id="password" required><br><br>
  <button type="submit">Login</button>
</form>
<p><a href="/wiki/register">Create an account</a></p>
</body>
</html>`);
});

app.post('/wiki/login', async (req, res) => {
    const { username, password } = req.body;
    try {
        const user = await User.findOne({ username });
        if (!user || !(await bcrypt.compare(password, user.password))) {
            return res.status(401).send('Invalid credentials. <a href="/wiki/login">Try again</a>');
        }
        const token = uuidv4();
        await new Session({ token, userId: user._id }).save();
        res.cookie('xp_session', token, { httpOnly: true });
        res.redirect('/');
    } catch (e) {
        res.status(500).send('An error occurred.');
    }
});

app.get('/wiki/register', (req, res) => {
    res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Register - XPlatform Wiki</title></head>
<body>
<h1>Create Account</h1>
<form action="/wiki/register" method="post">
  <label for="username">Username:</label><br>
  <input type="text" name="username" id="username" required><br><br>
  <label for="displayName">Display Name:</label><br>
  <input type="text" name="displayName" id="displayName" required><br><br>
  <label for="email">Email:</label><br>
  <input type="email" name="email" id="email"><br><br>
  <label for="password">Password:</label><br>
  <input type="password" name="password" id="password" required><br><br>
  <button type="submit">Register</button>
</form>
<p><a href="/wiki/login">Already have an account?</a></p>
</body>
</html>`);
});

app.post('/wiki/register', async (req, res) => {
    const { username, password, displayName, email } = req.body;
    try {
        const existing = await User.findOne({ username });
        if (existing) {
            return res.status(409).send('Username already taken. <a href="/wiki/register">Try again</a>');
        }
        const hashedPw = await bcrypt.hash(password, 10);
        const user = new User({
            username,
            password: hashedPw,
            displayName: displayName || username,
            email: email || '',
            isAdmin: false
        });
        await user.save();
        const token = uuidv4();
        await new Session({ token, userId: user._id }).save();
        res.cookie('xp_session', token, { httpOnly: true });
        res.redirect('/');
    } catch (e) {
        res.status(500).send('An error occurred.');
    }
});

app.get('/wiki/logout', (req, res) => {
    res.clearCookie('xp_session');
    res.redirect('/');
});

app.get('/wiki/profile', (req, res) => {
    if (!req.currentUser) return res.redirect('/wiki/login');
    const u = req.currentUser;
    res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Profile - XPlatform Wiki</title></head>
<body>
<h1>Profile: ${u.displayName}</h1>
<p>Username: ${u.username}</p>
<p>Email: ${u.email || 'Not set'}</p>
<p>Role: ${u.isAdmin ? 'Administrator' : 'User'}</p>
<p><a href="/">Back to Home</a></p>
</body>
</html>`);
});

// -----------------------------------------------------------
// Routes - Wiki Content
// -----------------------------------------------------------

app.get('/wiki/spaces', async (req, res) => {
    try {
        const spaces = await Space.find({});
        const spaceList = spaces.map(s => {
            const access = s.visibility === 'public' ? '🔓' : '🔒';
            return `<li>${access} <a href="/wiki/${s.name}/WebHome">${s.title || s.name}</a> - ${s.description || ''} <em>(${s.visibility})</em></li>`;
        }).join('\n');
        res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Spaces - XPlatform Wiki</title></head>
<body>
<h1>Wiki Spaces</h1>
<ul>${spaceList}</ul>
<p><a href="/">Back to Home</a></p>
</body>
</html>`);
    } catch (e) {
        res.status(500).send('An error occurred.');
    }
});

app.get('/wiki/:space/:docName', async (req, res) => {
    try {
        const doc = await WikiDocument.findOne({
            space: req.params.space,
            name: req.params.docName
        });
        if (!doc) {
            return res.status(404).send('Document not found.');
        }

        // Check access
        const space = await Space.findOne({ name: doc.space });
        if (space && space.visibility === 'private') {
            if (!req.currentUser || (!req.currentUser.isAdmin && space.owner.toString() !== req.currentUser._id.toString())) {
                return res.status(403).send('Access denied. You do not have permission to view this document.');
            }
        }

        res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>${doc.title} - XPlatform Wiki</title></head>
<body>
<h1>${doc.title}</h1>
<p class="meta">Space: ${doc.space} | Version: ${doc.version} | Last modified: ${doc.updatedAt.toISOString()}</p>
<hr>
<div class="content">${doc.content}</div>
<hr>
<p><a href="/wiki/spaces">Spaces</a> | <a href="/">Home</a></p>
</body>
</html>`);
    } catch (e) {
        res.status(500).send('An error occurred.');
    }
});

// -----------------------------------------------------------
// Routes - Search UI
// -----------------------------------------------------------

app.get('/wiki/search', (req, res) => {
    res.send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Search - XPlatform Wiki</title></head>
<body>
<h1>Search Wiki</h1>
<form action="/wiki/search" method="get">
  <input type="text" name="q" placeholder="Search documents..." value="${req.query.q || ''}" style="width:300px">
  <button type="submit">Search</button>
</form>
<p>For programmatic access, use the <a href="/wiki/api/search/suggest">Search Suggest API</a>.</p>
<div id="results"></div>
<script>
const q = new URLSearchParams(window.location.search).get('q');
if (q) {
    fetch('/wiki/api/search/suggest?media=json&input=' + encodeURIComponent(q) + '&query=' + encodeURIComponent('q=' + q))
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('results');
            if (data.results && data.results.length > 0) {
                el.innerHTML = '<h2>Results (' + data.numFound + ')</h2><ul>' +
                    data.results.map(r => '<li><a href="/wiki/' + r.space + '/' + r.name + '">' + (r.title || r.name) + '</a> <em>(' + r.space + ')</em></li>').join('') +
                    '</ul>';
            } else {
                el.innerHTML = '<p>No results found.</p>';
            }
        });
}
</script>
</body>
</html>`);
});

// -----------------------------------------------------------
// Routes - Search Suggest API (the core search endpoint)
// -----------------------------------------------------------

app.get('/wiki/api/search/suggest', async (req, res) => {
    try {
        const queryString = req.query.query || '';
        const input = req.query.input || '';
        const media = req.query.media || 'json';
        const nb = parseInt(req.query.nb) || 10;

        if (!queryString && !input) {
            return res.json({
                info: 'Search Suggest Service - provides search results for the search suggest UI component.',
                usage: 'Parameters: query (search query string with key=value pairs, one per line), input (search input text), nb (max results), media (json|xml)',
                examples: [
                    '/wiki/api/search/suggest?media=json&input=test&query=q%3Dtest',
                    '/wiki/api/search/suggest?media=json&input=+&query=q%3D*%3A*%0Afq%3Dtype%3ADOCUMENT'
                ]
            });
        }

        // Parse query parameters (key=value on each line)
        const params = {};
        const lines = queryString.split('\n');
        for (const line of lines) {
            const sepIdx = line.indexOf('=');
            if (sepIdx < 0) {
                if (!params.q) params.q = line;
            } else {
                const key = line.substring(0, sepIdx).trim();
                const value = line.substring(sepIdx + 1).trim();
                if (params[key]) {
                    if (!Array.isArray(params[key])) params[key] = [params[key]];
                    params[key].push(value);
                } else {
                    params[key] = value;
                }
            }
        }

        // Use input as search term if q not provided
        if (!params.q && input) {
            params.q = input;
        }

        // Build MongoDB query
        const searchQuery = params.q || '';
        const filterType = params.fq || null;
        const fieldList = params.fl || null;

        let mongoQuery = {};

        // Text search or wildcard
        if (searchQuery === '*' || searchQuery === '*:*') {
            mongoQuery = {}; // Match all
        } else if (searchQuery) {
            // Try text search, fall back to regex
            mongoQuery = {
                $or: [
                    { title: { $regex: searchQuery, $options: 'i' } },
                    { content: { $regex: searchQuery, $options: 'i' } },
                    { contentRaw: { $regex: searchQuery, $options: 'i' } },
                    { name: { $regex: searchQuery, $options: 'i' } },
                    { tags: { $regex: searchQuery, $options: 'i' } }
                ]
            };
        }

        // Apply filter query if present
        if (filterType) {
            const filters = Array.isArray(filterType) ? filterType : [filterType];
            for (const f of filters) {
                const fSep = f.indexOf(':');
                if (fSep > 0) {
                    const fKey = f.substring(0, fSep).trim();
                    const fVal = f.substring(fSep + 1).trim();
                    if (fKey === 'type') {
                        mongoQuery.type = fVal;
                    } else if (fKey === 'space') {
                        mongoQuery.space = fVal;
                    } else if (fKey === 'hidden') {
                        mongoQuery.hidden = fVal === 'true';
                    }
                }
            }
        }

        // Determine which fields to return
        let projection = null;
        if (fieldList) {
            projection = {};
            const fields = fieldList.split(',').map(f => f.trim()).filter(f => f);
            for (const f of fields) {
                // Map field names (handle trailing underscore pattern like Solr)
                const cleanField = f.replace(/_$/, '');
                projection[cleanField] = 1;
            }
            // Always include _id
            projection._id = 1;
        }

        // Execute query
        let results;
        if (projection) {
            results = await WikiDocument.find(mongoQuery, projection).limit(nb).lean();
        } else {
            results = await WikiDocument.find(mongoQuery).limit(nb).lean();
        }

        // Filter results based on access rights
        const { results: filteredResults, numFound } = await filterSearchResults(results, req.currentUser);

        // Format response
        if (media === 'json' || (req.headers.accept && req.headers.accept.includes('application/json'))) {
            res.json({
                numFound: numFound,
                results: filteredResults.map(doc => {
                    const out = {};
                    for (const key of Object.keys(doc)) {
                        if (key === '_id') {
                            out.id = doc._id.toString();
                        } else if (key === '__v') {
                            // skip
                        } else {
                            out[key] = doc[key];
                        }
                    }
                    return out;
                })
            });
        } else {
            // XML response
            let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<results>\n';
            for (const doc of filteredResults) {
                const id = doc._id ? doc._id.toString() : '';
                const docTitle = doc.title || doc.name || '';
                const docSpace = doc.space || '';
                xml += `  <rs id="${id}" type="DOCUMENT" space="${docSpace}">${docTitle}</rs>\n`;
            }
            xml += '</results>';
            res.type('text/xml').send(xml);
        }
    } catch (e) {
        res.status(500).json({ error: 'Search query failed.' });
    }
});

// -----------------------------------------------------------
// Health check
// -----------------------------------------------------------

app.get('/ping', (req, res) => {
    res.status(200).send('OK');
});

// -----------------------------------------------------------
// Start
// -----------------------------------------------------------

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/xplatform')
    .then(async () => {
        console.log('Connected to MongoDB');
        await seedDatabase();
        app.listen(PORT, () => {
            console.log(`XPlatform Wiki running on port ${PORT}`);
        });
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
        process.exit(1);
    });
