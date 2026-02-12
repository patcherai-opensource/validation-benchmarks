const express = require('express');
const mongoose = require('mongoose');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;

// Read flag from file planted at build time
const fs = require('fs');
let flag = 'flag{placeholder}';
try {
    flag = fs.readFileSync('/app/.flag_data', 'utf8').trim();
} catch(e) {
    // fallback
}

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/xwiki';

// Document schema - mirrors XWiki's Solr document structure
const DocumentSchema = new mongoose.Schema({
    title: { type: String, index: true },
    content: { type: String },
    space: { type: String, index: true },
    wiki: { type: String, default: 'xwiki' },
    author: { type: String },
    type: { type: String, default: 'DOCUMENT' },
    fullname: { type: String, index: true },
    reference: { type: String },
    hidden: { type: Boolean, default: false },
    locale: { type: String, default: 'en' },
    accessLevel: { type: String, default: 'public', enum: ['public', 'restricted', 'admin'] },
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
});

DocumentSchema.index({ title: 'text', content: 'text' });

const WikiDocument = mongoose.model('WikiDocument', DocumentSchema);

// User schema for authentication
const UserSchema = new mongoose.Schema({
    username: { type: String, unique: true },
    password: { type: String },
    displayName: { type: String },
    email: { type: String },
    groups: [{ type: String }],
    active: { type: Boolean, default: true },
    createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', UserSchema);

// Session schema
const SessionSchema = new mongoose.Schema({
    sessionId: { type: String, unique: true },
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    username: { type: String },
    createdAt: { type: Date, default: Date.now, expires: 3600 }
});

const Session = mongoose.model('Session', SessionSchema);

// Access rights cache - populated at startup from document metadata
// Maps fullname -> accessLevel for rights checking
const accessRightsCache = {};

// Middleware to resolve current user from session
async function resolveUser(req, res, next) {
    req.currentUser = null;
    const sessionId = req.cookies && req.cookies['JSESSIONID'];
    if (sessionId) {
        const session = await Session.findOne({ sessionId });
        if (session) {
            req.currentUser = { username: session.username, userId: session.userId };
        }
    }
    next();
}

app.use(resolveUser);

// Initialize wiki documents
async function initializeDocuments() {
    await WikiDocument.deleteMany({});
    await User.deleteMany({});
    await Session.deleteMany({});

    // Create default admin user
    const adminHash = crypto.createHash('sha256').update('admin_xwiki_secret_2024').digest('hex');
    await User.create({
        username: 'Admin',
        password: adminHash,
        displayName: 'Administrator',
        email: 'admin@xwiki.local',
        groups: ['XWiki.XWikiAdminGroup'],
        active: true
    });

    // Create guest user
    await User.create({
        username: 'XWikiGuest',
        password: '',
        displayName: 'Guest',
        email: '',
        groups: ['XWiki.XWikiAllGroup'],
        active: true
    });

    // Public documents - these are accessible to everyone
    const publicDocs = [
        {
            title: 'WebHome',
            content: 'Welcome to XWiki! This is a second generation wiki engine. XWiki offers a generic platform for developing collaborative web applications using the wiki paradigm.',
            space: 'Main',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'Main.WebHome',
            reference: 'xwiki:Main.WebHome',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'XWiki Syntax Guide',
            content: 'XWiki supports multiple syntaxes. The default syntax is XWiki Syntax 2.1. This guide covers the basics of formatting text, creating links, and embedding macros.',
            space: 'XWiki',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'XWiki.XWikiSyntax',
            reference: 'xwiki:XWiki.XWikiSyntax',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'Sandbox',
            content: 'This is a sandbox page where you can test wiki syntax. Feel free to edit this page to experiment with XWiki features.',
            space: 'Sandbox',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'Sandbox.WebHome',
            reference: 'xwiki:Sandbox.WebHome',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'User Directory',
            content: 'This page lists all registered users. Access the administration section for user management.',
            space: 'XWiki',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'XWiki.UserDirectory',
            reference: 'xwiki:XWiki.UserDirectory',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'Release Notes',
            content: 'XWiki Platform 14.10.12 - Release Notes. This release includes bug fixes and security patches. See JIRA for the complete list of resolved issues.',
            space: 'ReleaseNotes',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'ReleaseNotes.WebHome',
            reference: 'xwiki:ReleaseNotes.WebHome',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'FAQ',
            content: 'Frequently asked questions about XWiki platform. How to install extensions? Go to the Extension Manager in the Administration section.',
            space: 'FAQ',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'FAQ.WebHome',
            reference: 'xwiki:FAQ.WebHome',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'Developer Guide',
            content: 'This guide explains how to develop custom applications on XWiki. Topics include: Velocity scripting, Groovy scripting, REST API usage, and extension development.',
            space: 'DevGuide',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'DevGuide.WebHome',
            reference: 'xwiki:DevGuide.WebHome',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'SuggestSolrService',
            content: '{{velocity}}#set($discard = $services.search.solr.suggest($request)){{/velocity}}',
            space: 'XWiki',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'XWiki.SuggestSolrService',
            reference: 'xwiki:XWiki.SuggestSolrService',
            type: 'DOCUMENT',
            accessLevel: 'public'
        },
        {
            title: 'SuggestSolrMacros',
            content: '#macro(parseSearchSuggestParameters)## Parse parameters from request and build Solr query\n#set($queryParams = $request.query)\n#set($fieldList = $request.fl)\n#end',
            space: 'XWiki',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'XWiki.SuggestSolrMacros',
            reference: 'xwiki:XWiki.SuggestSolrMacros',
            type: 'DOCUMENT',
            accessLevel: 'public'
        }
    ];

    // Restricted documents - only accessible to admin/authenticated users with proper rights
    const restrictedDocs = [
        {
            title: 'Server Configuration',
            content: 'Database connection: jdbc:mysql://localhost:3306/xwiki. SMTP configuration: mail.smtp.host=smtp.xwiki.local. Clustering: disabled.',
            space: 'AdminConfig',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'AdminConfig.ServerConfig',
            reference: 'xwiki:AdminConfig.ServerConfig',
            type: 'DOCUMENT',
            accessLevel: 'restricted'
        },
        {
            title: 'Security Credentials',
            content: flag,
            space: 'AdminConfig',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'AdminConfig.SecurityCredentials',
            reference: 'xwiki:AdminConfig.SecurityCredentials',
            type: 'DOCUMENT',
            hidden: true,
            accessLevel: 'restricted'
        },
        {
            title: 'Backup Procedures',
            content: 'Daily backup schedule: 02:00 UTC. Backup location: /opt/xwiki/backups/. Retention policy: 30 days. Full backup on Sundays, incremental on weekdays.',
            space: 'AdminConfig',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'AdminConfig.BackupProcedures',
            reference: 'xwiki:AdminConfig.BackupProcedures',
            type: 'DOCUMENT',
            accessLevel: 'restricted'
        },
        {
            title: 'Internal Audit Log',
            content: 'Audit entries for 2024: User provisioning changes, permission matrix updates, SSO integration modifications. Contact security@xwiki.local for details.',
            space: 'AdminConfig',
            wiki: 'xwiki',
            author: 'XWiki.Admin',
            fullname: 'AdminConfig.AuditLog',
            reference: 'xwiki:AdminConfig.AuditLog',
            type: 'DOCUMENT',
            accessLevel: 'restricted'
        }
    ];

    const allDocs = [...publicDocs, ...restrictedDocs];
    await WikiDocument.insertMany(allDocs);

    // Build the access rights cache from document metadata
    for (const doc of allDocs) {
        if (doc.fullname) {
            accessRightsCache[doc.fullname] = doc.accessLevel || 'public';
        }
    }

    console.log(`Initialized ${allDocs.length} wiki documents, ${Object.keys(accessRightsCache).length} rights entries cached`);
}

/**
 * Filter Solr query response based on access rights.
 * This mirrors org.xwiki.query.solr.internal.SolrQueryExecutor.filterResponse()
 * 
 * The method checks each result document to verify the current user has VIEW rights.
 * It resolves the document reference from the result's space and fullname fields,
 * then looks up the access rights for that reference.
 */
function filterResponse(results, currentUser) {
    const filtered = [];

    for (const doc of results) {
        // Try to resolve the document reference for rights checking
        const resolvedRef = resolveDocumentReference(doc);

        if (resolvedRef === null) {
            // Cannot resolve reference - skip rights check for unresolvable entries
            filtered.push(doc);
            continue;
        }

        // Check if current user has VIEW rights on this document
        if (checkViewRights(resolvedRef, currentUser)) {
            filtered.push(doc);
        }
    }

    return filtered;
}

/**
 * Resolve a document reference from query result fields.
 * Requires 'space' and 'fullname' fields to be present in the result.
 * Returns null if the reference cannot be resolved.
 */
function resolveDocumentReference(doc) {
    // Both space and fullname are required to resolve the document reference
    if (!doc.space || !doc.fullname) {
        return null;
    }

    return {
        wiki: doc.wiki || 'xwiki',
        space: doc.space,
        fullname: doc.fullname,
        reference: doc.reference || `${doc.wiki || 'xwiki'}:${doc.fullname}`
    };
}

/**
 * Check if the current user has VIEW rights on the resolved document.
 * Uses the access rights cache to look up the document's access level by fullname.
 */
function checkViewRights(resolvedRef, currentUser) {
    // Admin users have access to everything
    if (currentUser && currentUser.username === 'Admin') {
        return true;
    }

    // Look up access level from the rights cache using the resolved fullname
    const docAccessLevel = accessRightsCache[resolvedRef.fullname];

    // If we found a rights entry, enforce it
    if (docAccessLevel === 'restricted' || docAccessLevel === 'admin') {
        return false;
    }

    // Default to allowing access for public or unknown documents
    return true;
}

/**
 * Execute a search query against documents, mimicking Solr query execution.
 * Parses the query string for Solr-like parameters.
 */
async function executeSearch(queryStr, fieldList, limit, inputStr) {
    let filter = {};

    // Parse query parameters (Solr-style)
    if (queryStr) {
        const lines = queryStr.split('\n');
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('fq=type:')) {
                filter.type = trimmed.replace('fq=type:', '');
            }
            if (trimmed.startsWith('fq=space:')) {
                filter.space = trimmed.replace('fq=space:', '');
            }
        }
    }

    // Add input-based search if provided
    if (inputStr && inputStr.trim()) {
        filter.$text = { $search: inputStr.trim() };
    }

    // Query all matching documents from MongoDB
    let results = await WikiDocument.find(filter).limit(limit || 100).lean();

    // Determine which fields to return
    let requestedFields = null;
    if (fieldList) {
        requestedFields = fieldList.split(',').map(f => f.trim());
    }

    // Solr field name aliases - maps Solr field names to document schema fields
    const fieldAliases = {
        'title_': 'title',
        'content_': 'content',
        'doccontentraw_': 'content',
        'objcontent__': 'content',
        'name_': 'title',
        'space_': 'space',
        'wiki_': 'wiki',
        'author_': 'author',
        'fullname_': 'fullname',
        'links': 'reference',
        'type': 'type',
        'hidden': 'hidden',
        'locale': 'locale'
    };

    // Project results to requested fields only (like Solr fl parameter)
    if (requestedFields) {
        results = results.map(doc => {
            const projected = {};
            for (const field of requestedFields) {
                // Direct field match
                if (doc[field] !== undefined) {
                    projected[field] = doc[field];
                }
                // Check aliases (e.g., title_ -> title, doccontentraw_ -> content)
                const alias = fieldAliases[field];
                if (alias && doc[alias] !== undefined && projected[field] === undefined) {
                    projected[field] = doc[alias];
                }
                // Handle trailing underscore as locale-specific field
                const baseField = field.replace(/_+$/, '');
                if (doc[baseField] !== undefined && projected[field] === undefined) {
                    projected[field] = doc[baseField];
                }
            }
            // Always include _id for internal tracking
            projected._id = doc._id;
            // Store access level internally for rights checking
            projected._accessLevel = doc.accessLevel;
            return projected;
        });
    } else {
        // Default field list includes space and fullname (needed for rights checks)
        results = results.map(doc => ({
            _id: doc._id,
            title: doc.title,
            space: doc.space,
            fullname: doc.fullname,
            reference: doc.reference,
            wiki: doc.wiki,
            type: doc.type,
            locale: doc.locale,
            _accessLevel: doc.accessLevel
        }));
    }

    return results;
}

/**
 * Clean internal fields from results before sending to client.
 */
function sanitizeResults(results) {
    return results.map(doc => {
        const clean = { ...doc };
        delete clean._accessLevel;
        delete clean._id;
        return clean;
    });
}

// ============================================
// Routes
// ============================================

// Main wiki page
app.get('/', (req, res) => {
    res.send(`<!DOCTYPE html>
<html>
<head><title>XWiki - Main - WebHome</title>
<style>
body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 0; }
.header { background: #2c3e50; color: white; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; }
.header a { color: #ecf0f1; text-decoration: none; margin-left: 15px; }
.content { padding: 20px; max-width: 1200px; margin: 0 auto; }
.nav { background: #34495e; padding: 8px 20px; }
.nav a { color: #bdc3c7; text-decoration: none; margin-right: 15px; font-size: 14px; }
.breadcrumb { padding: 10px 20px; background: #ecf0f1; font-size: 13px; }
.breadcrumb a { color: #2980b9; text-decoration: none; }
.panel { border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 4px; }
.panel h3 { margin-top: 0; color: #2c3e50; }
</style>
</head>
<body>
<div class="header">
    <div><strong>XWiki</strong> Platform 14.10.12</div>
    <div>
        ${req.currentUser ? '<span>Logged in as ' + req.currentUser.username + '</span> <a href="/xwiki/bin/logout/XWiki/XWikiLogout">Log out</a>' : '<a href="/xwiki/bin/login/XWiki/XWikiLogin">Log in</a> <a href="/xwiki/bin/register/XWiki/XWikiRegister">Register</a>'}
    </div>
</div>
<div class="nav">
    <a href="/">Home</a>
    <a href="/xwiki/bin/view/Sandbox/">Sandbox</a>
    <a href="/xwiki/bin/view/XWiki/XWikiSyntax">Syntax Guide</a>
    <a href="/xwiki/bin/view/FAQ/">FAQ</a>
    <a href="/xwiki/bin/view/DevGuide/">Developer Guide</a>
</div>
<div class="breadcrumb">
    <a href="/">Wiki</a> &raquo; <a href="/">Main</a> &raquo; WebHome
</div>
<div class="content">
    <h1>Welcome to XWiki</h1>
    <p>XWiki is a second generation wiki engine. XWiki offers a generic platform for developing collaborative web applications using the wiki paradigm.</p>
    
    <div class="panel">
        <h3>Getting Started</h3>
        <p>Explore the wiki using the navigation above. You can search for content using the search functionality.</p>
    </div>
    
    <div class="panel">
        <h3>Recent Activity</h3>
        <ul>
            <li>Release Notes updated - <em>XWiki Platform 14.10.12</em></li>
            <li>Developer Guide - New API documentation added</li>
            <li>FAQ section expanded with extension management guide</li>
        </ul>
    </div>
</div>
</body>
</html>`);
});

// View document
app.get('/xwiki/bin/view/:space/:page?', async (req, res) => {
    const space = req.params.space;
    const page = req.params.page || 'WebHome';
    const fullname = `${space}.${page}`;

    const doc = await WikiDocument.findOne({ fullname, accessLevel: 'public' });
    if (!doc) {
        return res.status(404).send(`<!DOCTYPE html>
<html><head><title>XWiki - Page Not Found</title></head>
<body>
<h1>Page not found</h1>
<p>The page <strong>${fullname}</strong> does not exist or you do not have permission to view it.</p>
<p><a href="/">Return to home</a></p>
</body></html>`);
    }

    res.send(`<!DOCTYPE html>
<html>
<head><title>XWiki - ${space} - ${page}</title>
<style>
body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 0; }
.header { background: #2c3e50; color: white; padding: 10px 20px; }
.nav { background: #34495e; padding: 8px 20px; }
.nav a { color: #bdc3c7; text-decoration: none; margin-right: 15px; font-size: 14px; }
.breadcrumb { padding: 10px 20px; background: #ecf0f1; font-size: 13px; }
.breadcrumb a { color: #2980b9; text-decoration: none; }
.content { padding: 20px; max-width: 1200px; margin: 0 auto; }
</style>
</head>
<body>
<div class="header"><strong>XWiki</strong> Platform 14.10.12</div>
<div class="nav">
    <a href="/">Home</a>
    <a href="/xwiki/bin/view/Sandbox/">Sandbox</a>
    <a href="/xwiki/bin/view/XWiki/XWikiSyntax">Syntax Guide</a>
</div>
<div class="breadcrumb">
    <a href="/">Wiki</a> &raquo; <a href="/xwiki/bin/view/${space}/">${space}</a> &raquo; ${page}
</div>
<div class="content">
    <h1>${doc.title}</h1>
    <div class="document-content">${doc.content}</div>
    <hr>
    <p style="font-size: 12px; color: #777;">Author: ${doc.author} | Last modified: ${doc.updatedAt ? doc.updatedAt.toISOString() : 'N/A'}</p>
</div>
</body></html>`);
});

// Login page
app.get('/xwiki/bin/login/XWiki/XWikiLogin', (req, res) => {
    res.send(`<!DOCTYPE html>
<html>
<head><title>XWiki - Log in</title>
<style>
body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 0; }
.header { background: #2c3e50; color: white; padding: 10px 20px; }
.content { padding: 40px; max-width: 400px; margin: 0 auto; }
input { width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box; }
button { padding: 10px 20px; background: #2980b9; color: white; border: none; cursor: pointer; }
.error { color: red; }
</style>
</head>
<body>
<div class="header"><strong>XWiki</strong> Platform 14.10.12</div>
<div class="content">
    <h1>Log in</h1>
    <form method="POST" action="/xwiki/bin/loginsubmit/XWiki/XWikiLogin">
        <label>Username:</label>
        <input type="text" name="j_username" required>
        <label>Password:</label>
        <input type="password" name="j_password" required>
        <button type="submit">Log in</button>
    </form>
    <p><a href="/">Return to home</a></p>
</div>
</body></html>`);
});

// Login submit
app.post('/xwiki/bin/loginsubmit/XWiki/XWikiLogin', async (req, res) => {
    const { j_username, j_password } = req.body;
    const hash = crypto.createHash('sha256').update(j_password || '').digest('hex');
    const user = await User.findOne({ username: j_username, password: hash, active: true });

    if (!user) {
        return res.status(401).send(`<!DOCTYPE html>
<html><head><title>XWiki - Login Failed</title></head>
<body><h1>Login failed</h1><p>Invalid credentials.</p><p><a href="/xwiki/bin/login/XWiki/XWikiLogin">Try again</a></p></body></html>`);
    }

    const sessionId = crypto.randomBytes(32).toString('hex');
    await Session.create({ sessionId, userId: user._id, username: user.username });
    res.cookie('JSESSIONID', sessionId, { httpOnly: true });
    res.redirect('/');
});

// Logout
app.get('/xwiki/bin/logout/XWiki/XWikiLogout', async (req, res) => {
    const sessionId = req.cookies && req.cookies['JSESSIONID'];
    if (sessionId) {
        await Session.deleteOne({ sessionId });
    }
    res.clearCookie('JSESSIONID');
    res.redirect('/');
});

// Registration page
app.get('/xwiki/bin/register/XWiki/XWikiRegister', (req, res) => {
    res.send(`<!DOCTYPE html>
<html>
<head><title>XWiki - Register</title>
<style>
body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 0; }
.header { background: #2c3e50; color: white; padding: 10px 20px; }
.content { padding: 40px; max-width: 400px; margin: 0 auto; }
input { width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box; }
button { padding: 10px 20px; background: #27ae60; color: white; border: none; cursor: pointer; }
</style>
</head>
<body>
<div class="header"><strong>XWiki</strong> Platform 14.10.12</div>
<div class="content">
    <h1>Register a new account</h1>
    <form method="POST" action="/xwiki/bin/register/XWiki/XWikiRegister">
        <label>Username:</label>
        <input type="text" name="register_username" required>
        <label>Password:</label>
        <input type="password" name="register_password" required>
        <label>Confirm Password:</label>
        <input type="password" name="register_password2" required>
        <label>Email:</label>
        <input type="email" name="register_email">
        <button type="submit">Register</button>
    </form>
    <p><a href="/xwiki/bin/login/XWiki/XWikiLogin">Already have an account? Log in</a></p>
</div>
</body></html>`);
});

// Registration submit
app.post('/xwiki/bin/register/XWiki/XWikiRegister', async (req, res) => {
    const { register_username, register_password, register_password2, register_email } = req.body;

    if (!register_username || !register_password) {
        return res.status(400).send('Username and password are required.');
    }
    if (register_password !== register_password2) {
        return res.status(400).send('Passwords do not match.');
    }

    const existing = await User.findOne({ username: register_username });
    if (existing) {
        return res.status(409).send('Username already taken.');
    }

    const hash = crypto.createHash('sha256').update(register_password).digest('hex');
    await User.create({
        username: register_username,
        password: hash,
        displayName: register_username,
        email: register_email || '',
        groups: ['XWiki.XWikiAllGroup'],
        active: true
    });

    res.redirect('/xwiki/bin/login/XWiki/XWikiLogin');
});

// REST API - Search
app.get('/xwiki/rest/search', async (req, res) => {
    const query = req.query.q || '';
    const limit = parseInt(req.query.number) || 10;

    // Only search public documents via REST
    const results = await WikiDocument.find({
        accessLevel: 'public',
        $text: { $search: query }
    }).limit(limit).lean();

    res.json({
        searchResults: results.map(doc => ({
            title: doc.title,
            space: doc.space,
            fullname: doc.fullname,
            reference: doc.reference
        }))
    });
});

/**
 * SuggestSolrService endpoint.
 * Provides search suggestions via Solr backend integration.
 * See XWiki.SuggestSolrMacros for the Velocity macro implementation.
 * 
 * Parameters:
 *   - query: Solr query string (can contain q, fq, fl parameters)
 *   - fl: field list to return
 *   - nb: number of results
 *   - input: search input string
 *   - media: response format (json)
 *   - outputSyntax: output syntax (plain)
 */
app.get('/xwiki/bin/get/XWiki/SuggestSolrService', async (req, res) => {
    try {
        const queryStr = req.query.query || '';
        const fieldList = req.query.fl || null;
        const nb = parseInt(req.query.nb) || 10;
        const input = req.query.input || '';
        const media = req.query.media || 'json';
        const outputSyntax = req.query.outputSyntax || 'plain';

        // Parse any fl from within the query string itself (Solr-style multi-line params)
        let effectiveFieldList = fieldList;
        if (queryStr) {
            const lines = queryStr.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed.startsWith('fl=')) {
                    effectiveFieldList = trimmed.substring(3);
                }
            }
        }

        // Execute the search query
        let results = await executeSearch(queryStr, effectiveFieldList, nb, input);

        // Apply access rights filtering
        results = filterResponse(results, req.currentUser);

        // Remove internal fields before returning
        const cleanResults = sanitizeResults(results);

        if (media === 'json') {
            res.json({
                responseHeader: { status: 0, params: {} },
                response: {
                    numFound: cleanResults.length,
                    start: 0,
                    docs: cleanResults
                }
            });
        } else {
            res.type('text/plain').send(JSON.stringify({
                response: {
                    numFound: cleanResults.length,
                    docs: cleanResults
                }
            }));
        }
    } catch (err) {
        res.status(500).json({
            responseHeader: { status: 500 },
            error: { msg: 'Internal query execution error' }
        });
    }
});

// REST API endpoints for wiki management
app.get('/xwiki/rest/wikis/xwiki/spaces', async (req, res) => {
    const spaces = await WikiDocument.distinct('space', { accessLevel: 'public' });
    res.json({ spaces: spaces.map(s => ({ name: s, home: `${s}.WebHome` })) });
});

app.get('/xwiki/rest/wikis/xwiki/spaces/:space/pages', async (req, res) => {
    const docs = await WikiDocument.find({
        space: req.params.space,
        accessLevel: 'public'
    }).select('title fullname reference').lean();

    res.json({ pageSummaries: docs.map(d => ({ title: d.title, fullName: d.fullname })) });
});

// Admin panel - requires authentication
app.get('/xwiki/bin/admin/XWiki/XWikiPreferences', async (req, res) => {
    if (!req.currentUser || req.currentUser.username !== 'Admin') {
        return res.status(403).send(`<!DOCTYPE html>
<html><head><title>XWiki - Access Denied</title></head>
<body><h1>Access Denied</h1><p>You do not have permission to access the administration panel.</p>
<p><a href="/xwiki/bin/login/XWiki/XWikiLogin">Log in</a></p></body></html>`);
    }

    res.send(`<!DOCTYPE html>
<html>
<head><title>XWiki - Administration</title>
<style>
body { font-family: Helvetica, Arial, sans-serif; margin: 0; }
.header { background: #2c3e50; color: white; padding: 10px 20px; }
.content { padding: 20px; }
</style>
</head>
<body>
<div class="header"><strong>XWiki</strong> Administration</div>
<div class="content">
    <h1>Administration</h1>
    <ul>
        <li><a href="/xwiki/bin/admin/XWiki/XWikiPreferences?section=users">User Management</a></li>
        <li><a href="/xwiki/bin/admin/XWiki/XWikiPreferences?section=rights">Rights Management</a></li>
        <li><a href="/xwiki/bin/admin/XWiki/XWikiPreferences?section=extensions">Extension Manager</a></li>
    </ul>
</div>
</body></html>`);
});

// Health check endpoint
app.get('/ping', (req, res) => {
    res.status(200).send('pong');
});

// Start the server
const startServer = () => {
    app.listen(PORT, () => {
        console.log(`XWiki Platform running on http://localhost:${PORT}`);
    });
};

mongoose.connect(MONGODB_URI)
    .then(async () => {
        console.log('Connected to MongoDB');
        await initializeDocuments();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });
