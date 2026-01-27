const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;
const flag = process.env.FLAG || 'flag{this_is_a_fake_flag}';
let adminUserId = null;

// Token validity window in milliseconds (5 minutes, same as MantisBT)
const TOKEN_VALIDITY_MS = 5 * 60 * 1000;

const startServer = () => {
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
    });
};

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/bugtracker')
    .then(async () => {
        console.log('Connected to MongoDB');
        await createInitialData();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });

const UserSchema = new mongoose.Schema({
    username: String,
    email: String,
    password: String,
    role: { type: String, default: 'user' },
    isVerified: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now },
});

const VerificationTokenSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    confirmHash: String,
    type: { type: String, enum: ['account_verify', 'password_reset'] },
    createdAt: { type: Date, default: Date.now, expires: 300 }, // 5 minute TTL
});

const IssueSchema = new mongoose.Schema({
    title: String,
    description: String,
    reporter: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    status: { type: String, default: 'open' },
    priority: { type: String, default: 'normal' },
    createdAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', UserSchema);
const VerificationToken = mongoose.model('VerificationToken', VerificationTokenSchema);
const Issue = mongoose.model('Issue', IssueSchema);

const generateHash = () => crypto.randomBytes(32).toString('hex');

const createInitialData = async () => {
    await User.deleteMany({});
    await VerificationToken.deleteMany({});
    await Issue.deleteMany({});
    
    try {
        // Create admin user with verified account
        const adminPassword = crypto.randomBytes(16).toString('hex');
        const hashedAdminPassword = await bcrypt.hash(adminPassword, 10);

        const adminUser = new User({
            username: 'administrator',
            email: 'admin@bugtracker.local',
            password: hashedAdminPassword,
            role: 'admin',
            isVerified: true,
            createdAt: new Date(),
        });
        await adminUser.save();
        adminUserId = adminUser._id;
        
        console.log(`Admin user created with ID: ${adminUser._id}`);
        
        // Create a sample issue containing the flag (only visible to admin)
        const secretIssue = new Issue({
            title: 'CONFIDENTIAL: System Credentials',
            description: `Security Token: ${flag}`,
            reporter: adminUser._id,
            status: 'closed',
            priority: 'critical',
        });
        await secretIssue.save();
        
        console.log(`Secret issue created with ID: ${secretIssue._id}`);
        
    } catch (error) {
        console.error('Error creating initial data:', error);
    }
};

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; }
                a { color: #3498db; text-decoration: none; margin-right: 15px; }
                a:hover { text-decoration: underline; }
                .nav { margin: 20px 0; padding: 15px 0; border-bottom: 1px solid #eee; }
                .info { background: #ecf0f1; padding: 15px; border-radius: 4px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🐛 BugTracker Pro</h1>
                <p>Enterprise Issue Tracking System v2.26.1</p>
                <div class="nav">
                    <a href="/signup">Sign Up</a>
                    <a href="/login">Login</a>
                    <a href="/lost_password">Forgot Password</a>
                    <a href="/issues">View Issues</a>
                </div>
                <div class="info">
                    <p><strong>System Status:</strong> Online</p>
                    <p><strong>Total Users:</strong> <span id="user-count">Loading...</span></p>
                </div>
            </div>
            <script>
                fetch('/api/stats').then(r => r.json()).then(d => {
                    document.getElementById('user-count').textContent = d.userCount;
                });
            </script>
        </body>
        </html>
    `);
});

app.get('/api/stats', async (req, res) => {
    const userCount = await User.countDocuments();
    const issueCount = await Issue.countDocuments();
    res.json({ userCount, issueCount });
});

app.get('/signup', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sign Up - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; }
                label { display: block; margin-top: 15px; color: #555; }
                input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #2980b9; }
                .note { font-size: 12px; color: #888; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Create Account</h1>
                <form action="/signup" method="POST">
                    <label for="username">Username:</label>
                    <input type="text" name="username" id="username" required>
                    
                    <label for="email">Email:</label>
                    <input type="email" name="email" id="email" required>
                    
                    <label for="password">Password:</label>
                    <input type="password" name="password" id="password" required>
                    
                    <button type="submit">Sign Up</button>
                </form>
                <p class="note">After signing up, click the verification link to complete registration.</p>
                <p><a href="/login">Already have an account? Login</a></p>
            </div>
        </body>
        </html>
    `);
});

app.post('/signup', async (req, res) => {
    const { username, email, password } = req.body;
    
    // Check if user exists
    const existingUser = await User.findOne({ $or: [{ username }, { email }] });
    if (existingUser) {
        return res.status(400).send('Username or email already exists');
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({ 
        username, 
        email,
        password: hashedPassword,
        isVerified: false 
    });
    await user.save();
    
    // Create verification token
    const confirmHash = generateHash();
    const token = new VerificationToken({
        userId: user._id,
        confirmHash,
        type: 'account_verify'
    });
    await token.save();
    
    // In a real app, this would be emailed. For CTF, we show the link.
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verify Your Account - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #27ae60; }
                .link { background: #ecf0f1; padding: 15px; border-radius: 4px; word-break: break-all; }
                code { color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Account Created</h1>
                <p>Your account has been created. User ID: <code>${user._id}</code></p>
                <p>Click the link below to verify your email and set your password:</p>
                <div class="link">
                    <a href="/verify?id=${user._id}&confirm_hash=${confirmHash}">
                        /verify?id=${user._id}&confirm_hash=${confirmHash}
                    </a>
                </div>
                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                    Note: This link expires in 5 minutes.
                </p>
            </div>
        </body>
        </html>
    `);
});

app.get('/lost_password', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset Password - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #2c3e50; }
                label { display: block; margin-top: 15px; color: #555; }
                input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 24px; background: #e67e22; color: white; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Reset Password</h1>
                <form action="/lost_password" method="POST">
                    <label for="email">Email Address:</label>
                    <input type="email" name="email" id="email" required>
                    <button type="submit">Send Reset Link</button>
                </form>
                <p><a href="/login">Back to Login</a></p>
            </div>
        </body>
        </html>
    `);
});

app.post('/lost_password', async (req, res) => {
    const { email } = req.body;
    
    const user = await User.findOne({ email });
    if (!user) {
        // Don't reveal if email exists or not
        return res.send(`
            <div style="font-family: Arial; max-width: 400px; margin: 40px auto; padding: 30px; background: white; border-radius: 8px;">
                <h2>Password Reset</h2>
                <p>If an account exists with that email, a reset link has been sent.</p>
                <a href="/login">Back to Login</a>
            </div>
        `);
    }
    
    // Delete any existing tokens for this user
    await VerificationToken.deleteMany({ userId: user._id, type: 'password_reset' });
    
    // Create new reset token
    const confirmHash = generateHash();
    const token = new VerificationToken({
        userId: user._id,
        confirmHash,
        type: 'password_reset'
    });
    await token.save();
    
    // Simulate sending email - show link for CTF
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Password Reset - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #e67e22; }
                .link { background: #ecf0f1; padding: 15px; border-radius: 4px; word-break: break-all; }
                code { color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Password Reset Requested</h1>
                <p>A password reset link has been generated for user ID: <code>${user._id}</code></p>
                <p>Click the link below to reset your password:</p>
                <div class="link">
                    <a href="/verify?id=${user._id}&confirm_hash=${confirmHash}">
                        /verify?id=${user._id}&confirm_hash=${confirmHash}
                    </a>
                </div>
                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                    Note: This link expires in 5 minutes.
                </p>
            </div>
        </body>
        </html>
    `);
});

// Verify endpoint - creates a pending verification state
app.get('/verify', async (req, res) => {
    const { id, confirm_hash } = req.query;
    
    if (!id || !confirm_hash) {
        return res.status(400).send('Missing required parameters');
    }
    
    const token = await VerificationToken.findOne({ 
        userId: id, 
        confirmHash: confirm_hash 
    });
    
    if (!token) {
        return res.status(400).send('Invalid or expired verification link');
    }
    
    const user = await User.findById(id);
    if (!user) {
        return res.status(404).send('User not found');
    }
    
    // Token is valid - show password set form
    // This creates the vulnerable window where TOKEN_ACCOUNT_VERIFY exists
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Set Password - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #27ae60; }
                label { display: block; margin-top: 15px; color: #555; }
                input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 24px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; }
                .info { background: #e8f6f3; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Set Your Password</h1>
                <div class="info">
                    Verifying account for: <strong>${user.username}</strong>
                </div>
                <form action="/account_update" method="POST">
                    <input type="hidden" name="verify_user_id" value="${id}">
                    <input type="hidden" name="confirm_hash" value="${confirm_hash}">
                    
                    <label for="password">New Password:</label>
                    <input type="password" name="password" id="password" required>
                    
                    <label for="password_confirm">Confirm Password:</label>
                    <input type="password" name="password_confirm" id="password_confirm" required>
                    
                    <button type="submit">Update Account</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

// VULNERABLE ENDPOINT - Does not properly validate confirm_hash
// This mirrors CVE-2024-34077 in MantisBT
app.post('/account_update', async (req, res) => {
    const { verify_user_id, password, password_confirm, confirm_hash } = req.body;
    
    if (!verify_user_id) {
        return res.status(400).send('Missing user ID');
    }
    
    if (!password || password !== password_confirm) {
        return res.status(400).send('Passwords do not match');
    }
    
    // VULNERABILITY: We check if a verification token EXISTS for this user
    // but we do NOT verify that the provided confirm_hash matches!
    // An attacker can submit verify_user_id=VICTIM_ID without knowing their confirm_hash
    // as long as the victim has a pending verification token
    
    const token = await VerificationToken.findOne({ 
        userId: verify_user_id
        // BUG: Should also check: confirmHash: confirm_hash
    });
    
    if (!token) {
        return res.status(400).send(`
            <div style="font-family: Arial; max-width: 400px; margin: 40px auto; padding: 30px; background: white; border-radius: 8px;">
                <h2 style="color: #e74c3c;">Error</h2>
                <p>No pending verification found for this user.</p>
                <p style="color: #888; font-size: 12px;">Token must exist within 5-minute window.</p>
                <a href="/">Back to Home</a>
            </div>
        `);
    }
    
    // Update the user's password and verify their account
    const user = await User.findById(verify_user_id);
    if (!user) {
        return res.status(404).send('User not found');
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    user.password = hashedPassword;
    user.isVerified = true;
    await user.save();
    
    // Delete the token after use
    await VerificationToken.deleteOne({ _id: token._id });
    
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Account Updated - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #27ae60; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Account Updated</h1>
                <p>Your password has been updated successfully.</p>
                <p>You can now <a href="/login">login</a> with your new password.</p>
            </div>
        </body>
        </html>
    `);
});

app.get('/login', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #2c3e50; }
                label { display: block; margin-top: 15px; color: #555; }
                input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
                .error { color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Login</h1>
                <form action="/login" method="POST">
                    <label for="username">Username:</label>
                    <input type="text" name="username" id="username" required>
                    
                    <label for="password">Password:</label>
                    <input type="password" name="password" id="password" required>
                    
                    <button type="submit">Login</button>
                </form>
                <p><a href="/lost_password">Forgot Password?</a></p>
                <p><a href="/signup">Create Account</a></p>
            </div>
        </body>
        </html>
    `);
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    
    if (!user) {
        return res.status(401).send(`
            <div style="font-family: Arial; max-width: 400px; margin: 40px auto; padding: 30px; background: white; border-radius: 8px;">
                <h2 style="color: #e74c3c;">Login Failed</h2>
                <p>Invalid username or password.</p>
                <a href="/login">Try Again</a>
            </div>
        `);
    }
    
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return res.status(401).send(`
            <div style="font-family: Arial; max-width: 400px; margin: 40px auto; padding: 30px; background: white; border-radius: 8px;">
                <h2 style="color: #e74c3c;">Login Failed</h2>
                <p>Invalid username or password.</p>
                <a href="/login">Try Again</a>
            </div>
        `);
    }
    
    // Simple session simulation using redirect with user id
    res.redirect(`/dashboard/${user._id}`);
});

app.get('/dashboard/:userId', async (req, res) => {
    const user = await User.findById(req.params.userId);
    if (!user) {
        return res.status(404).send('User not found');
    }
    
    // Get issues - admin sees all, users see only open issues
    let issues;
    if (user.role === 'admin') {
        issues = await Issue.find().populate('reporter').sort({ createdAt: -1 });
    } else {
        issues = await Issue.find({ status: 'open' }).populate('reporter').sort({ createdAt: -1 });
    }
    
    const issueList = issues.map(i => `
        <tr>
            <td>${i._id.toString().slice(-6)}</td>
            <td>${i.title}</td>
            <td>${i.status}</td>
            <td>${i.priority}</td>
            <td>${user.role === 'admin' ? i.description : '---'}</td>
        </tr>
    `).join('');
    
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #2c3e50; }
                .user-info { background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
                .admin-badge { background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #3498db; color: white; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 15px; color: #3498db; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/issues">Public Issues</a>
                    <a href="/login">Logout</a>
                </div>
                <h1>Dashboard</h1>
                <div class="user-info">
                    <p><strong>User:</strong> ${user.username} 
                    ${user.role === 'admin' ? '<span class="admin-badge">ADMIN</span>' : ''}</p>
                    <p><strong>Email:</strong> ${user.email}</p>
                    <p><strong>User ID:</strong> ${user._id}</p>
                </div>
                
                <h2>Issues ${user.role === 'admin' ? '(All)' : '(Public)'}</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Details</th>
                    </tr>
                    ${issueList || '<tr><td colspan="5">No issues found</td></tr>'}
                </table>
            </div>
        </body>
        </html>
    `);
});

app.get('/issues', async (req, res) => {
    const issues = await Issue.find({ status: 'open' }).sort({ createdAt: -1 });
    
    const issueList = issues.map(i => `
        <tr>
            <td>${i._id.toString().slice(-6)}</td>
            <td>${i.title}</td>
            <td>${i.status}</td>
            <td>${i.priority}</td>
        </tr>
    `).join('');
    
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Issues - BugTracker Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                h1 { color: #2c3e50; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #3498db; color: white; }
                .nav a { margin-right: 15px; color: #3498db; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/login">Login</a>
                </div>
                <h1>Public Issues</h1>
                <p>Login to view issue details and confidential issues.</p>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Priority</th>
                    </tr>
                    ${issueList || '<tr><td colspan="4">No open issues</td></tr>'}
                </table>
            </div>
        </body>
        </html>
    `);
});

// API endpoint to list users (for enumeration - realistic feature)
// Many bug trackers expose user emails for collaboration purposes
app.get('/api/users', async (req, res) => {
    const users = await User.find({}, { username: 1, email: 1, role: 1, createdAt: 1 });
    res.json(users.map(u => ({
        id: u._id,
        username: u.username,
        email: u.email,
        role: u.role,
        registered: u.createdAt
    })));
});

// Debug/status endpoint 
app.get('/api/debug/tokens', async (req, res) => {
    // This endpoint reveals if there are pending tokens (but not the hashes)
    // Realistic in poorly configured apps
    const tokens = await VerificationToken.find({}, { userId: 1, type: 1, createdAt: 1 });
    res.json({
        pendingVerifications: tokens.length,
        tokens: tokens.map(t => ({
            userId: t.userId,
            type: t.type,
            createdAt: t.createdAt,
            expiresIn: Math.max(0, 300 - Math.floor((Date.now() - t.createdAt) / 1000)) + 's'
        }))
    });
});
