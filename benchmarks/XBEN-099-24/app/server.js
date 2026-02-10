const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const session = require('express-session');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;
const flag = process.env.FLAG || 'flag{this_is_a_fake_flag}';

const startServer = () => {
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
    });
};

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/ezplatform')
    .then(async () => {
        console.log('Connected to MongoDB');
        await initializeDatabase();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });

const UserSchema = new mongoose.Schema({
    contentId: { type: Number, unique: true },
    username: String,
    email: String,
    firstName: String,
    lastName: String,
    password: String,
    role: { type: String, default: 'member' },
    enabled: { type: Boolean, default: true },
    versionInfo: {
        versionNo: { type: Number, default: 1 },
        language: { type: String, default: 'eng-GB' },
        status: { type: String, default: 'published' },
        lastModified: { type: Date, default: Date.now }
    },
    createdAt: { type: Date, default: Date.now },
    notes: { type: String, default: '' }
});

const User = mongoose.model('User', UserSchema);

let nextContentId = 10;

const initializeDatabase = async () => {
    await User.deleteMany({});
    
    const adminPassword = crypto.randomBytes(16).toString('hex');
    const hashedAdminPassword = await bcrypt.hash(adminPassword, 10);
    
    const adminUser = new User({
        contentId: 1,
        username: 'admin',
        email: 'admin@ezplatform.local',
        firstName: 'System',
        lastName: 'Administrator',
        password: hashedAdminPassword,
        role: 'administrator',
        enabled: true,
        versionInfo: {
            versionNo: 1,
            language: 'eng-GB',
            status: 'published',
            lastModified: new Date()
        },
        notes: flag
    });
    await adminUser.save();
    
    const sampleUsers = [
        { contentId: 2, username: 'editor', email: 'editor@company.com', firstName: 'Jane', lastName: 'Editor', role: 'editor' },
        { contentId: 3, username: 'jsmith', email: 'john.smith@company.com', firstName: 'John', lastName: 'Smith', role: 'member' },
        { contentId: 4, username: 'mwilson', email: 'mary.wilson@company.com', firstName: 'Mary', lastName: 'Wilson', role: 'member' },
        { contentId: 5, username: 'rjohnson', email: 'robert.johnson@company.com', firstName: 'Robert', lastName: 'Johnson', role: 'contributor' }
    ];
    
    for (const userData of sampleUsers) {
        const hashedPassword = await bcrypt.hash(crypto.randomBytes(12).toString('hex'), 10);
        const user = new User({
            ...userData,
            password: hashedPassword,
            versionInfo: {
                versionNo: 1,
                language: 'eng-GB',
                status: 'published',
                lastModified: new Date()
            }
        });
        await user.save();
    }
    
    nextContentId = 10;
    console.log('Database initialized with sample users');
};

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(session({
    secret: crypto.randomBytes(32).toString('hex'),
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false, httpOnly: true, maxAge: 3600000 }
}));

const requireAuth = (req, res, next) => {
    if (!req.session || !req.session.userId) {
        return res.status(401).send('Unauthorized - Please log in');
    }
    next();
};

const requireAdmin = async (req, res, next) => {
    if (!req.session || !req.session.userId) {
        return res.status(401).send('Unauthorized');
    }
    const user = await User.findOne({ contentId: req.session.userId });
    if (!user || user.role !== 'administrator') {
        return res.status(403).send('Forbidden - Administrator access required');
    }
    next();
};

app.get('/', (req, res) => {
    const isLoggedIn = req.session && req.session.userId;
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>eZ Platform - Content Management</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
                .header { background: #1a1a2e; color: white; padding: 20px; }
                .header h1 { margin: 0; }
                .nav { background: #16213e; padding: 10px 20px; }
                .nav a { color: #eee; margin-right: 20px; text-decoration: none; }
                .nav a:hover { color: #fff; text-decoration: underline; }
                .content { padding: 40px; max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>eZ Platform</h1>
                <p>Enterprise Content Management System</p>
            </div>
            <div class="nav">
                <a href="/">Home</a>
                ${isLoggedIn ? `
                    <a href="/admin/dashboard">Dashboard</a>
                    <a href="/admin/users">Users</a>
                    <a href="/logout">Logout</a>
                ` : `
                    <a href="/login">Login</a>
                `}
            </div>
            <div class="content">
                <div class="card">
                    <h2>Welcome to eZ Platform</h2>
                    <p>eZ Platform is a professional CMS for building content-rich websites and applications.</p>
                    ${!isLoggedIn ? '<p><a href="/login">Please log in</a> to access the administration panel.</p>' : ''}
                </div>
            </div>
        </body>
        </html>
    `);
});

app.get('/login', (req, res) => {
    if (req.session && req.session.userId) {
        return res.redirect('/admin/dashboard');
    }
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; background: #1a1a2e; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); width: 350px; }
                .login-box h2 { margin-top: 0; color: #1a1a2e; }
                .form-group { margin-bottom: 15px; }
                .form-group label { display: block; margin-bottom: 5px; color: #333; }
                .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                .btn { width: 100%; padding: 12px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                .btn:hover { background: #16213e; }
                .error { color: #dc3545; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>eZ Platform Login</h2>
                ${req.query.error ? '<p class="error">Invalid credentials</p>' : ''}
                <form action="/login" method="post">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" name="username" id="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" name="password" id="password" required>
                    </div>
                    <button type="submit" class="btn">Sign In</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (!user) {
        return res.redirect('/login?error=1');
    }
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return res.redirect('/login?error=1');
    }
    req.session.userId = user.contentId;
    req.session.username = user.username;
    req.session.role = user.role;
    res.redirect('/admin/dashboard');
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});

app.get('/admin/dashboard', requireAuth, async (req, res) => {
    const userCount = await User.countDocuments();
    const user = await User.findOne({ contentId: req.session.userId });
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
                .header { background: #1a1a2e; color: white; padding: 20px; }
                .nav { background: #16213e; padding: 10px 20px; }
                .nav a { color: #eee; margin-right: 20px; text-decoration: none; }
                .content { padding: 40px; max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
                .stats { display: flex; gap: 20px; }
                .stat-box { background: #1a1a2e; color: white; padding: 20px; border-radius: 5px; text-align: center; flex: 1; }
                .stat-box h3 { margin: 0; font-size: 36px; }
                .stat-box p { margin: 10px 0 0 0; opacity: 0.8; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>eZ Platform Administration</h1>
            </div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/admin/dashboard">Dashboard</a>
                <a href="/admin/users">Users</a>
                <a href="/logout">Logout (${user.username})</a>
            </div>
            <div class="content">
                <div class="card">
                    <h2>Welcome, ${user.firstName} ${user.lastName}</h2>
                    <p>Role: ${user.role}</p>
                </div>
                <div class="stats">
                    <div class="stat-box">
                        <h3>${userCount}</h3>
                        <p>Total Users</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.get('/admin/users', requireAuth, async (req, res) => {
    const users = await User.find({}, { password: 0 }).sort({ contentId: 1 });
    const currentUser = await User.findOne({ contentId: req.session.userId });
    
    let userRows = users.map(u => `
        <tr>
            <td>${u.contentId}</td>
            <td>${u.username}</td>
            <td>${u.firstName} ${u.lastName}</td>
            <td>${u.email}</td>
            <td>${u.role}</td>
            <td>
                ${currentUser.role === 'administrator' ? `<a href="/admin/user/edit/${u.contentId}">Edit</a>` : '-'}
            </td>
        </tr>
    `).join('');
    
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Users - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
                .header { background: #1a1a2e; color: white; padding: 20px; }
                .nav { background: #16213e; padding: 10px 20px; }
                .nav a { color: #eee; margin-right: 20px; text-decoration: none; }
                .content { padding: 40px; max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #f8f8f8; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>User Management</h1>
            </div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/admin/dashboard">Dashboard</a>
                <a href="/admin/users">Users</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="content">
                <div class="card">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${userRows}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.get('/admin/user/edit/:contentId', requireAdmin, async (req, res) => {
    const contentId = parseInt(req.params.contentId);
    const user = await User.findOne({ contentId }, { password: 0 });
    
    if (!user) {
        return res.status(404).send('User not found');
    }
    
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Edit User - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
                .header { background: #1a1a2e; color: white; padding: 20px; }
                .nav { background: #16213e; padding: 10px 20px; }
                .nav a { color: #eee; margin-right: 20px; text-decoration: none; }
                .content { padding: 40px; max-width: 800px; margin: 0 auto; }
                .card { background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .form-group { margin-bottom: 20px; }
                .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                .btn { padding: 12px 24px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Edit User: ${user.username}</h1>
            </div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/admin/dashboard">Dashboard</a>
                <a href="/admin/users">Users</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="content">
                <div class="card">
                    <form action="/admin/user/update/${user.contentId}" method="post">
                        <div class="form-group">
                            <label>Content ID</label>
                            <input type="text" value="${user.contentId}" disabled>
                        </div>
                        <div class="form-group">
                            <label>Username</label>
                            <input type="text" name="username" value="${user.username}">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" name="email" value="${user.email}">
                        </div>
                        <div class="form-group">
                            <label>First Name</label>
                            <input type="text" name="firstName" value="${user.firstName}">
                        </div>
                        <div class="form-group">
                            <label>Last Name</label>
                            <input type="text" name="lastName" value="${user.lastName}">
                        </div>
                        <div class="form-group">
                            <label>Role</label>
                            <select name="role">
                                <option value="member" ${user.role === 'member' ? 'selected' : ''}>Member</option>
                                <option value="contributor" ${user.role === 'contributor' ? 'selected' : ''}>Contributor</option>
                                <option value="editor" ${user.role === 'editor' ? 'selected' : ''}>Editor</option>
                                <option value="administrator" ${user.role === 'administrator' ? 'selected' : ''}>Administrator</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Notes</label>
                            <textarea name="notes" rows="3">${user.notes || ''}</textarea>
                        </div>
                        <button type="submit" class="btn">Update User</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.post('/admin/user/update/:contentId', requireAdmin, async (req, res) => {
    const contentId = parseInt(req.params.contentId);
    const { username, email, firstName, lastName, role, notes } = req.body;
    
    await User.updateOne(
        { contentId },
        { 
            username, email, firstName, lastName, role, notes,
            'versionInfo.versionNo': { $inc: 1 },
            'versionInfo.lastModified': new Date()
        }
    );
    
    res.redirect('/admin/users');
});

app.get('/user/update/:contentId/:versionNo/:language', async (req, res) => {
    const contentId = parseInt(req.params.contentId);
    const versionNo = parseInt(req.params.versionNo);
    const language = req.params.language;
    
    const user = await User.findOne({ contentId }, { password: 0 });
    
    if (!user) {
        return res.status(404).send('Content not found');
    }
    
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Edit User - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
                .header { background: #1a1a2e; color: white; padding: 20px; }
                .nav { background: #16213e; padding: 10px 20px; }
                .nav a { color: #eee; margin-right: 20px; text-decoration: none; }
                .content { padding: 40px; max-width: 800px; margin: 0 auto; }
                .card { background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .form-group { margin-bottom: 20px; }
                .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                .btn { padding: 12px 24px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; }
                .meta-info { background: #f8f8f8; padding: 15px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Edit Content</h1>
            </div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/login">Login</a>
            </div>
            <div class="content">
                <div class="card">
                    <div class="meta-info">
                        <strong>Content ID:</strong> ${user.contentId} | 
                        <strong>Version:</strong> ${user.versionInfo.versionNo} | 
                        <strong>Language:</strong> ${user.versionInfo.language} |
                        <strong>Status:</strong> ${user.versionInfo.status}
                    </div>
                    <form action="/user/update/${user.contentId}/${versionNo}/${language}" method="post">
                        <div class="form-group">
                            <label>Username</label>
                            <input type="text" name="username" value="${user.username}">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" name="email" value="${user.email}">
                        </div>
                        <div class="form-group">
                            <label>First Name</label>
                            <input type="text" name="firstName" value="${user.firstName}">
                        </div>
                        <div class="form-group">
                            <label>Last Name</label>
                            <input type="text" name="lastName" value="${user.lastName}">
                        </div>
                        <div class="form-group">
                            <label>Role</label>
                            <select name="role">
                                <option value="member" ${user.role === 'member' ? 'selected' : ''}>Member</option>
                                <option value="contributor" ${user.role === 'contributor' ? 'selected' : ''}>Contributor</option>
                                <option value="editor" ${user.role === 'editor' ? 'selected' : ''}>Editor</option>
                                <option value="administrator" ${user.role === 'administrator' ? 'selected' : ''}>Administrator</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Notes</label>
                            <textarea name="notes" rows="3">${user.notes || ''}</textarea>
                        </div>
                        <button type="submit" class="btn">Update</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.post('/user/update/:contentId/:versionNo/:language', async (req, res) => {
    const contentId = parseInt(req.params.contentId);
    
    const user = await User.findOne({ contentId });
    if (!user) {
        return res.status(404).send('Content not found');
    }
    
    return res.status(403).send('Permission denied - You do not have permission to edit this content');
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Internal Server Error');
});

app.use((req, res) => {
    res.status(404).send('Not Found');
});
