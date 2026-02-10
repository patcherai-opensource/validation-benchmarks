const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const Database = require('better-sqlite3');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize SQLite database
const dbPath = path.join(__dirname, 'data', 'plugins.db');
if (!fs.existsSync(path.dirname(dbPath))) {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
}
const db = new Database(dbPath);

// Initialize database tables
db.exec(`
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS plugins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source TEXT NOT NULL,
        location TEXT,
        version TEXT,
        status TEXT DEFAULT 'pending',
        installed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
`);

// Create default admin user if not exists
const adminExists = db.prepare('SELECT * FROM users WHERE username = ?').get('admin');
if (!adminExists) {
    db.prepare('INSERT INTO users (username, password, role) VALUES (?, ?, ?)').run('admin', 'admin', 'admin');
}

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(session({
    secret: uuidv4(),
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false, maxAge: 3600000 }
}));

// Plugin installation directory
const PLUGINS_DIR = path.join(__dirname, 'installed_plugins');
const TEMP_DIR = path.join(__dirname, 'temp');

if (!fs.existsSync(PLUGINS_DIR)) {
    fs.mkdirSync(PLUGINS_DIR, { recursive: true });
}
if (!fs.existsSync(TEMP_DIR)) {
    fs.mkdirSync(TEMP_DIR, { recursive: true });
}

// Auth middleware
const isAuthenticated = (req, res, next) => {
    if (req.session && req.session.userId) {
        return next();
    }
    return res.redirect('/login');
};

const isAdmin = (req, res, next) => {
    if (req.session && req.session.userId) {
        const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.session.userId);
        if (user && user.role === 'admin') {
            req.user = user;
            return next();
        }
    }
    return res.status(403).send('Access denied. Admin privileges required.');
};

// Routes
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Plugin Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 15px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Plugin Management System</h1>
                <p>Welcome to the Plugin Manager. Manage your application plugins with ease.</p>
                <div class="nav">
                    ${req.session.userId ? 
                        '<a href="/dashboard">Dashboard</a> <a href="/logout">Logout</a>' : 
                        '<a href="/login">Login</a>'}
                </div>
                <h3>Features</h3>
                <ul>
                    <li>Install plugins from Git repositories</li>
                    <li>Install plugins from NPM registry</li>
                    <li>Manage installed plugins</li>
                    <li>Plugin version control</li>
                </ul>
            </div>
        </body>
        </html>
    `);
});

app.get('/login', (req, res) => {
    if (req.session.userId) {
        return res.redirect('/dashboard');
    }
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Plugin Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; }
                input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .error { color: red; text-align: center; }
                a { display: block; text-align: center; margin-top: 15px; color: #007bff; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Admin Login</h1>
                ${req.query.error ? '<p class="error">Invalid credentials</p>' : ''}
                <form method="POST" action="/login">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
    `);
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const user = db.prepare('SELECT * FROM users WHERE username = ? AND password = ?').get(username, password);
    
    if (user) {
        req.session.userId = user.id;
        req.session.username = user.username;
        req.session.role = user.role;
        return res.redirect('/dashboard');
    }
    res.redirect('/login?error=1');
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});

app.get('/dashboard', isAuthenticated, (req, res) => {
    const plugins = db.prepare('SELECT * FROM plugins ORDER BY installed_at DESC').all();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.session.userId);
    
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - Plugin Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1, h2 { color: #333; }
                .nav { margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #eee; }
                .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #f8f9fa; }
                .btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
                .btn-primary { background: #007bff; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .status-installed { color: green; }
                .status-pending { color: orange; }
                .status-failed { color: red; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    ${user.role === 'admin' ? '<a href="/plugins">Install Plugin</a>' : ''}
                    <a href="/logout">Logout</a>
                    <span style="float: right;">Logged in as: <strong>${user.username}</strong> (${user.role})</span>
                </div>
                
                <h1>Dashboard</h1>
                <h2>Installed Plugins</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Source</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Installed</th>
                            ${user.role === 'admin' ? '<th>Actions</th>' : ''}
                        </tr>
                    </thead>
                    <tbody>
                        ${plugins.length === 0 ? '<tr><td colspan="6">No plugins installed yet.</td></tr>' :
                            plugins.map(p => `
                                <tr>
                                    <td>${escapeHtml(p.name)}</td>
                                    <td>${p.source}</td>
                                    <td>${p.location || '-'}</td>
                                    <td class="status-${p.status}">${p.status}</td>
                                    <td>${new Date(p.installed_at).toLocaleString()}</td>
                                    ${user.role === 'admin' ? `<td><a href="/plugins/delete/${p.id}" class="btn btn-danger" onclick="return confirm('Delete this plugin?')">Delete</a></td>` : ''}
                                </tr>
                            `).join('')}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
    `);
});

app.get('/plugins', isAdmin, (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Install Plugin - Plugin Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .nav { margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #eee; }
                .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
                label { display: block; margin-top: 15px; font-weight: bold; }
                input[type="text"], select { width: 100%; padding: 10px; margin: 5px 0 15px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #218838; }
                .help-text { font-size: 12px; color: #666; margin-top: -10px; }
                .message { padding: 10px; border-radius: 4px; margin-bottom: 15px; }
                .message.error { background: #f8d7da; color: #721c24; }
                .message.success { background: #d4edda; color: #155724; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/dashboard">Dashboard</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <h1>Install New Plugin</h1>
                
                ${req.query.error ? `<div class="message error">${escapeHtml(req.query.error)}</div>` : ''}
                ${req.query.success ? `<div class="message success">Plugin installation initiated successfully!</div>` : ''}
                
                <form method="POST" action="/plugins">
                    <label for="name">Plugin Name</label>
                    <input type="text" id="name" name="name" placeholder="my-plugin" required>
                    <p class="help-text">A unique name for the plugin</p>
                    
                    <label for="source">Installation Source</label>
                    <select id="source" name="source" required>
                        <option value="">Select source...</option>
                        <option value="git">Git Repository</option>
                        <option value="npm">NPM Registry</option>
                        <option value="local">Local Path</option>
                    </select>
                    
                    <label for="location">Source Location</label>
                    <input type="text" id="location" name="location" placeholder="https://github.com/user/repo.git">
                    <p class="help-text">Git URL, NPM package name, or local path</p>
                    
                    <button type="submit">Install Plugin</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

// Plugin installation endpoint
app.post('/plugins', isAdmin, (req, res) => {
    const { name, source, location } = req.body;
    
    if (!name || !source) {
        return res.redirect('/plugins?error=Plugin name and source are required');
    }
    
    // Create plugin installer instance
    const installer = new PluginInstaller({ name, source, location });
    
    try {
        const result = installer.install();
        
        // Save to database
        db.prepare('INSERT INTO plugins (name, source, location, status) VALUES (?, ?, ?, ?)').run(
            name,
            source,
            location || '',
            result.success ? 'installed' : 'failed'
        );
        
        if (result.success) {
            return res.redirect('/plugins?success=1');
        } else {
            return res.redirect(`/plugins?error=${encodeURIComponent(result.message)}`);
        }
    } catch (err) {
        db.prepare('INSERT INTO plugins (name, source, location, status) VALUES (?, ?, ?, ?)').run(
            name,
            source,
            location || '',
            'failed'
        );
        return res.redirect(`/plugins?error=${encodeURIComponent('Installation failed')}`);
    }
});

app.get('/plugins/delete/:id', isAdmin, (req, res) => {
    const { id } = req.params;
    db.prepare('DELETE FROM plugins WHERE id = ?').run(id);
    res.redirect('/dashboard');
});

// Plugin Installer class
class PluginInstaller {
    constructor(pluginConfig) {
        this.name = pluginConfig.name;
        this.source = pluginConfig.source;
        this.location = pluginConfig.location;
        this.tempDir = path.join(TEMP_DIR, this.name);
        this.pluginDir = path.join(PLUGINS_DIR, this.name);
    }
    
    install() {
        // Prepare plugin directories
        this.prepPluginsFolder();
        
        switch (this.source) {
            case 'git':
                return this.installFromGit();
            case 'npm':
                return this.installFromNpm();
            case 'local':
                return this.installFromLocal();
            default:
                return { success: false, message: 'Unknown source type' };
        }
    }
    
    prepPluginsFolder() {
        // Create temp directory for this plugin
        try {
            if (!fs.existsSync(this.tempDir)) {
                fs.mkdirSync(this.tempDir, { recursive: true });
            }
        } catch (e) {
            // Directory creation may fail for some names
        }
        // Plugin directory will be created by git clone
    }
    
    installFromGit() {
        if (!this.location) {
            return { success: false, message: 'Git URL is required' };
        }
        
        try {
            gitPullOrClone(this.location, this.pluginDir);
            return { success: true, message: 'Plugin installed from Git' };
        } catch (err) {
            return { success: false, message: 'Git clone failed' };
        }
    }
    
    installFromNpm() {
        if (!this.location) {
            return { success: false, message: 'NPM package name is required' };
        }
        
        try {
            execSync(`npm pack ${this.location}`, { 
                cwd: this.tempDir, 
                timeout: 30000,
                stdio: 'pipe'
            });
            return { success: true, message: 'Plugin installed from NPM' };
        } catch (err) {
            return { success: false, message: 'NPM installation failed' };
        }
    }
    
    installFromLocal() {
        if (!this.location) {
            return { success: false, message: 'Local path is required' };
        }
        return { success: false, message: 'Local installation not yet implemented' };
    }
}

// Git utility functions
function gitPullOrClone(gitUrl, pluginDir) {
    const gitDir = path.join(pluginDir, '.git');
    
    if (fs.existsSync(gitDir)) {
        const cmd = `cd ${pluginDir} && git pull`;
        execSync(cmd, { timeout: 60000, stdio: 'pipe' });
    } else {
        const cmd = `git clone ${gitUrl} ${pluginDir}`;
        execSync(cmd, { timeout: 60000, stdio: 'pipe' });
    }
}

// HTML escape utility
function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Serve installed plugin files (for plugin assets like JS, CSS, images)
app.use('/plugins/files', express.static(PLUGINS_DIR));

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).send('Not Found');
});

// Global error handler - don't expose stack traces
app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).send('Internal Server Error');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Plugin Manager running on port ${PORT}`);
});
