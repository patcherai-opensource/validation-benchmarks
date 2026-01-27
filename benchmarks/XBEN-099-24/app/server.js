const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

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
        await createInitialContent();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });

// Counter for sequential content IDs
const CounterSchema = new mongoose.Schema({
    _id: String,
    seq: { type: Number, default: 0 }
});
const Counter = mongoose.model('Counter', CounterSchema);

const getNextContentId = async () => {
    const counter = await Counter.findByIdAndUpdate(
        'contentId',
        { $inc: { seq: 1 } },
        { new: true, upsert: true }
    );
    return counter.seq;
};

// User content schema with sequential contentId
const UserContentSchema = new mongoose.Schema({
    contentId: { type: Number, unique: true, index: true },
    login: String,
    email: String,
    firstName: String,
    lastName: String,
    password: String,
    enabled: { type: Boolean, default: true },
    versionNo: { type: Number, default: 1 },
    mainLanguageCode: { type: String, default: 'eng-GB' },
    createdAt: { type: Date, default: Date.now },
    modifiedAt: { type: Date, default: Date.now }
});

const UserContent = mongoose.model('UserContent', UserContentSchema);

// Store admin contentId
let adminContentId = null;

const createInitialContent = async () => {
    await UserContent.deleteMany({});
    await Counter.deleteMany({});
    
    try {
        // Create admin user with contentId 14 (common eZ Platform admin ID)
        await Counter.findByIdAndUpdate('contentId', { seq: 13 }, { upsert: true });
        
        const adminId = await getNextContentId(); // Will be 14
        const hashedPassword = await bcrypt.hash('admin_secret_2024!', 10);

        const adminUser = new UserContent({
            contentId: adminId,
            login: 'admin',
            email: flag, // Flag is stored in admin's email
            firstName: 'Administrator',
            lastName: 'System',
            password: hashedPassword,
            enabled: true,
            versionNo: 1,
            mainLanguageCode: 'eng-GB'
        });
        await adminUser.save();
        adminContentId = adminId;
        
        console.log(`Admin user created with contentId: ${adminId}`);

        // Create a few more sample users
        for (let i = 0; i < 3; i++) {
            const userId = await getNextContentId();
            const hashedPwd = await bcrypt.hash(`user${i}_pass`, 10);
            const sampleUser = new UserContent({
                contentId: userId,
                login: `editor${i}`,
                email: `editor${i}@ezplatform.local`,
                firstName: `Editor`,
                lastName: `User${i}`,
                password: hashedPwd,
                enabled: true,
                versionNo: 1
            });
            await sampleUser.save();
            console.log(`Sample user created with contentId: ${userId}`);
        }
    } catch (error) {
        console.error('Error creating initial content:', error);
    }
};

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Home page - eZ Platform style
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>eZ Platform - Content Management</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
                .header { background: #1a1a2e; color: white; padding: 20px; }
                .header h1 { margin: 0; font-size: 24px; }
                .nav { background: #16213e; padding: 10px 20px; }
                .nav a { color: #a0a0a0; text-decoration: none; margin-right: 20px; }
                .nav a:hover { color: white; }
                .container { padding: 40px; max-width: 1200px; margin: 0 auto; }
                .card { background: white; border-radius: 4px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                .btn { background: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>eZ Platform</h1>
            </div>
            <div class="nav">
                <a href="/">Dashboard</a>
                <a href="/content/browse">Content</a>
                <a href="/user/list">Users</a>
                <a href="/admin/login">Admin Login</a>
            </div>
            <div class="container">
                <div class="card">
                    <h2>Welcome to eZ Platform CMS</h2>
                    <p>eZ Platform is a modern, open-source content management system built on Symfony framework.</p>
                    <p>Version: 2.3.0 | repository-forms: 2.3.1</p>
                </div>
                <div class="card">
                    <h3>Quick Links</h3>
                    <p><a href="/admin/login" class="btn">Admin Login</a></p>
                </div>
            </div>
            <div class="footer">
                &copy; 2024 eZ Platform. All rights reserved. | <a href="/api/info">API Info</a>
            </div>
        </body>
        </html>
    `);
});

// Content browse page
app.get('/content/browse', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Content Browser - eZ Platform</title></head>
        <body>
            <h1>Content Browser</h1>
            <p>Please <a href="/admin/login">login</a> to browse content.</p>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
    `);
});

// User list page (requires auth in production, but shows list here)
app.get('/user/list', async (req, res) => {
    const users = await UserContent.find({}, 'contentId login firstName lastName enabled').sort({ contentId: 1 });
    
    let userRows = users.map(u => `
        <tr>
            <td>${u.contentId}</td>
            <td>${u.login}</td>
            <td>${u.firstName} ${u.lastName}</td>
            <td>${u.enabled ? 'Active' : 'Disabled'}</td>
            <td><a href="/admin/login">Edit</a></td>
        </tr>
    `).join('');

    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Management - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #1a1a2e; color: white; }
            </style>
        </head>
        <body>
            <h1>User Management</h1>
            <p>Registered users in the system:</p>
            <table>
                <tr>
                    <th>Content ID</th>
                    <th>Login</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
                ${userRows}
            </table>
            <p><a href="/">Back to Home</a></p>
            <!-- Note: User edit forms available at /user/update/{contentId}/{versionNo}/{language} -->
        </body>
        </html>
    `);
});

// Admin login page
app.get('/admin/login', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; background: #1a1a2e; height: 100vh; display: flex; align-items: center; justify-content: center; }
                .login-box { background: white; padding: 40px; border-radius: 8px; width: 300px; }
                .login-box h2 { margin-top: 0; }
                .form-group { margin-bottom: 15px; }
                .form-group label { display: block; margin-bottom: 5px; }
                .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                .btn { background: #0d6efd; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>eZ Platform Admin</h2>
                <form action="/admin/login" method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="login" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Sign In</button>
                </form>
                <p style="margin-top: 20px; text-align: center;"><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    `);
});

// Admin login POST handler
app.post('/admin/login', async (req, res) => {
    const { login, password } = req.body;
    const user = await UserContent.findOne({ login });
    
    if (!user) {
        return res.status(401).send('Invalid credentials. <a href="/admin/login">Try again</a>');
    }
    
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return res.status(401).send('Invalid credentials. <a href="/admin/login">Try again</a>');
    }
    
    // In a real app, would set session. Here just redirect to dashboard
    res.redirect('/admin/dashboard?user=' + user.login);
});

// Admin dashboard (simplified)
app.get('/admin/dashboard', (req, res) => {
    const user = req.query.user || 'guest';
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard - eZ Platform</title></head>
        <body>
            <h1>Welcome, ${user}</h1>
            <p>Dashboard features coming soon.</p>
            <p><a href="/">Home</a> | <a href="/user/list">User List</a></p>
        </body>
        </html>
    `);
});

// VULNERABLE ENDPOINT - Missing authorization check
// This endpoint should require authentication and permission check
// but currently allows any user to access any user's edit form
app.get('/user/update/:contentId/:versionNo/:language', async (req, res) => {
    const { contentId, versionNo, language } = req.params;
    
    // Load user by contentId without checking permissions
    // VULNERABILITY: No authentication or authorization check here!
    const user = await UserContent.findOne({ contentId: parseInt(contentId) });
    
    if (!user) {
        return res.status(404).send(`
            <!DOCTYPE html>
            <html>
            <head><title>Error - eZ Platform</title></head>
            <body>
                <h1>Content Not Found</h1>
                <p>The requested content (ID: ${contentId}) was not found.</p>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
        `);
    }
    
    // Return user edit form with user data (including email!)
    // This exposes sensitive user information without authorization
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Edit User - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
                .form-container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
                .form-group { margin-bottom: 20px; }
                .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                .form-group input[readonly] { background: #f0f0f0; }
                .btn { background: #0d6efd; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                .meta { color: #666; font-size: 12px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="form-container">
                <h1>Edit User Content</h1>
                <div class="meta">
                    Content ID: ${user.contentId} | Version: ${user.versionNo} | Language: ${user.mainLanguageCode}
                </div>
                <form action="/user/update/${contentId}/${versionNo}/${language}" method="POST">
                    <div class="form-group">
                        <label>Login</label>
                        <input type="text" name="login" value="${user.login}" readonly>
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
                        <label>Enabled</label>
                        <input type="checkbox" name="enabled" ${user.enabled ? 'checked' : ''}>
                    </div>
                    <button type="submit" class="btn">Update User</button>
                </form>
                <p style="margin-top: 20px;"><a href="/user/list">Back to User List</a> | <a href="/">Home</a></p>
            </div>
        </body>
        </html>
    `);
});

// POST handler for user update (also vulnerable but returns error)
app.post('/user/update/:contentId/:versionNo/:language', async (req, res) => {
    // In this demo, we don't actually update - just show a message
    res.status(403).send(`
        <!DOCTYPE html>
        <html>
        <head><title>Error - eZ Platform</title></head>
        <body>
            <h1>Permission Denied</h1>
            <p>You do not have permission to modify this content.</p>
            <p>Please contact your administrator.</p>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
    `);
});

// API info endpoint
app.get('/api/info', (req, res) => {
    res.json({
        platform: 'eZ Platform',
        version: '2.3.0',
        repository_forms: '2.3.1',
        api_endpoints: [
            { path: '/user/list', method: 'GET', description: 'List all users' },
            { path: '/user/update/{contentId}/{versionNo}/{language}', method: 'GET', description: 'User edit form' },
            { path: '/admin/login', method: 'GET/POST', description: 'Admin authentication' }
        ],
        note: 'Some endpoints may require authentication'
    });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});
