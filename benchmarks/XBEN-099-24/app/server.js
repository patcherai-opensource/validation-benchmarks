const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const session = require('express-session');

const app = express();
const PORT = process.env.PORT || 3000;
const flag = process.env.FLAG || 'flag{this_is_a_fake_flag}';
let adminUserId = null;

const TOKEN_VALIDITY_MS = 5 * 60 * 1000; // 5 minutes

const startServer = () => {
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
    });
};

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/bugtracker')
    .then(async () => {
        console.log('Connected to MongoDB');
        await initializeDatabase();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });

const UserSchema = new mongoose.Schema({
    username: { type: String, unique: true, required: true },
    email: { type: String, unique: true, required: true },
    password: String,
    realname: String,
    role: { type: String, default: 'reporter' },
    enabled: { type: Boolean, default: true },
    createdAt: { type: Date, default: Date.now },
});

const VerificationTokenSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    confirmHash: { type: String, required: true },
    type: { type: String, enum: ['account_verify', 'password_reset'], required: true },
    createdAt: { type: Date, default: Date.now, expires: 300 }
});

const IssueSchema = new mongoose.Schema({
    title: String,
    description: String,
    status: { type: String, default: 'new' },
    priority: { type: String, default: 'normal' },
    reporter: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    assignee: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    createdAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', UserSchema);
const VerificationToken = mongoose.model('VerificationToken', VerificationTokenSchema);
const Issue = mongoose.model('Issue', IssueSchema);

const initializeDatabase = async () => {
    await User.deleteMany({});
    await VerificationToken.deleteMany({});
    await Issue.deleteMany({});
    
    try {
        const adminPassword = crypto.randomBytes(16).toString('hex');
        const hashedPassword = await bcrypt.hash(adminPassword, 10);

        const adminUser = new User({
            username: 'administrator',
            email: 'admin@bugtracker.local',
            password: hashedPassword,
            realname: 'System Administrator',
            role: 'administrator',
            enabled: true,
        });
        await adminUser.save();
        adminUserId = adminUser._id;
        
        console.log(`Admin user created with ID: ${adminUser._id}`);

        const reporterPassword = crypto.randomBytes(16).toString('hex');
        const hashedReporterPass = await bcrypt.hash(reporterPassword, 10);
        
        const reporter = new User({
            username: 'reporter1',
            email: 'reporter@bugtracker.local', 
            password: hashedReporterPass,
            realname: 'Test Reporter',
            role: 'reporter',
            enabled: true,
        });
        await reporter.save();

        const issue = new Issue({
            title: 'Initial setup complete',
            description: 'System has been initialized successfully.',
            status: 'resolved',
            priority: 'low',
            reporter: reporter._id,
        });
        await issue.save();

    } catch (error) {
        console.error('Error initializing database:', error);
    }
};

const generateConfirmHash = () => {
    return crypto.randomBytes(32).toString('hex');
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
    if (!req.session.userId) {
        return res.redirect('/login');
    }
    next();
};

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>BugTracker - Issue Management System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                nav { margin: 20px 0; }
                nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
                nav a:hover { text-decoration: underline; }
                .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>BugTracker</h1>
                <p>Welcome to BugTracker - Your Issue Management System</p>
                <nav>
                    <a href="/login">Login</a>
                    <a href="/signup">Sign Up</a>
                    <a href="/lost_password">Forgot Password</a>
                </nav>
                <div class="info">
                    <p>BugTracker helps teams track and manage software issues efficiently.</p>
                    <p>Please login or create an account to get started.</p>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.get('/signup', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sign Up - BugTracker</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                form { margin-top: 20px; }
                label { display: block; margin-top: 15px; font-weight: bold; }
                input[type="text"], input[type="email"], input[type="password"] { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 30px; background: #0066cc; color: white; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #0052a3; }
                .link { margin-top: 15px; }
                .link a { color: #0066cc; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Create Account</h1>
                <form action="/signup" method="post">
                    <label for="username">Username:</label>
                    <input type="text" name="username" id="username" required>
                    
                    <label for="email">Email:</label>
                    <input type="email" name="email" id="email" required>
                    
                    <label for="realname">Real Name:</label>
                    <input type="text" name="realname" id="realname">
                    
                    <button type="submit">Sign Up</button>
                </form>
                <div class="link">
                    <a href="/login">Already have an account? Login</a>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.post('/signup', async (req, res) => {
    const { username, email, realname } = req.body;
    
    try {
        const existingUser = await User.findOne({ $or: [{ username }, { email }] });
        if (existingUser) {
            return res.status(400).send('Username or email already exists');
        }

        const tempPassword = crypto.randomBytes(8).toString('hex');
        const hashedPassword = await bcrypt.hash(tempPassword, 10);
        
        const user = new User({
            username,
            email,
            password: hashedPassword,
            realname: realname || username,
            enabled: false, 
        });
        await user.save();

        const confirmHash = generateConfirmHash();
        const token = new VerificationToken({
            userId: user._id,
            confirmHash,
            type: 'account_verify',
        });
        await token.save();

        console.log(`Verification email would be sent to ${email} with link: /verify.php?id=${user._id}&confirm_hash=${confirmHash}`);

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Registration Pending - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    .success { background: #d4edda; padding: 15px; border-radius: 5px; color: #155724; }
                    .info { margin-top: 15px; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Registration Pending</h1>
                    <div class="success">
                        <p>Account created successfully!</p>
                        <p>A verification email has been sent to <strong>${email}</strong>.</p>
                    </div>
                    <div class="info">
                        <p>Please check your email and click the verification link to complete your registration.</p>
                        <p>The link will expire in 5 minutes.</p>
                        <p>Your user ID is: <strong>${user._id}</strong></p>
                    </div>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('Signup error:', error);
        res.status(500).send('Registration failed');
    }
});

app.get('/verify.php', async (req, res) => {
    const { id, confirm_hash } = req.query;
    
    if (!id || !confirm_hash) {
        return res.status(400).send('Invalid verification link');
    }

    try {
        const token = await VerificationToken.findOne({ 
            userId: id, 
            confirmHash: confirm_hash,
            type: { $in: ['account_verify', 'password_reset'] }
        });

        if (!token) {
            return res.status(400).send('Invalid or expired verification link');
        }

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Set Password - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    form { margin-top: 20px; }
                    label { display: block; margin-top: 15px; font-weight: bold; }
                    input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
                    button { margin-top: 20px; padding: 12px 30px; background: #0066cc; color: white; border: none; border-radius: 3px; cursor: pointer; }
                    button:hover { background: #0052a3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Set Your Password</h1>
                    <p>Please enter a new password for your account.</p>
                    <form action="/account_update.php" method="post">
                        <input type="hidden" name="verify_user_id" value="${id}">
                        <input type="hidden" name="confirm_hash" value="${confirm_hash}">
                        
                        <label for="password">New Password:</label>
                        <input type="password" name="password" id="password" required>
                        
                        <label for="password_confirm">Confirm Password:</label>
                        <input type="password" name="password_confirm" id="password_confirm" required>
                        
                        <label for="realname">Real Name:</label>
                        <input type="text" name="realname" id="realname">
                        
                        <button type="submit">Update Account</button>
                    </form>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('Verification error:', error);
        res.status(500).send('Verification failed');
    }
});

app.post('/account_update.php', async (req, res) => {
    const { verify_user_id, password, password_confirm, realname, email } = req.body;

    if (!verify_user_id) {
        return res.status(400).send('Invalid request');
    }

    if (!password || !password_confirm) {
        return res.status(400).send('Password is required');
    }

    if (password !== password_confirm) {
        return res.status(400).send('Passwords do not match');
    }

    try {
        const token = await VerificationToken.findOne({ 
            userId: verify_user_id,
            type: { $in: ['account_verify', 'password_reset'] }
        });

        if (!token) {
            return res.status(400).send('No pending verification found for this user');
        }

        const user = await User.findById(verify_user_id);
        if (!user) {
            return res.status(404).send('User not found');
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        user.password = hashedPassword;
        user.enabled = true;
        
        if (realname) {
            user.realname = realname;
        }
        if (email) {
            user.email = email;
        }
        
        await user.save();
        await VerificationToken.deleteMany({ userId: verify_user_id });

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Account Updated - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    .success { background: #d4edda; padding: 15px; border-radius: 5px; color: #155724; }
                    .link { margin-top: 20px; }
                    .link a { color: #0066cc; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Account Updated</h1>
                    <div class="success">
                        <p>Your account has been successfully updated!</p>
                        <p>You can now login with your new password.</p>
                    </div>
                    <div class="link">
                        <a href="/login">Go to Login</a>
                    </div>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('Account update error:', error);
        res.status(500).send('Account update failed');
    }
});

app.get('/lost_password', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset Password - BugTracker</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                form { margin-top: 20px; }
                label { display: block; margin-top: 15px; font-weight: bold; }
                input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 30px; background: #0066cc; color: white; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #0052a3; }
                .link { margin-top: 15px; }
                .link a { color: #0066cc; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Reset Password</h1>
                <p>Enter your username or email to reset your password.</p>
                <form action="/lost_password" method="post">
                    <label for="username">Username or Email:</label>
                    <input type="text" name="username" id="username" required>
                    
                    <button type="submit">Reset Password</button>
                </form>
                <div class="link">
                    <a href="/login">Back to Login</a>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.post('/lost_password', async (req, res) => {
    const { username } = req.body;
    
    try {
        const user = await User.findOne({ 
            $or: [{ username }, { email: username }] 
        });

        if (!user) {
            return res.send(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Password Reset - BugTracker</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                        h1 { color: #333; }
                        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Password Reset</h1>
                        <div class="info">
                            <p>If an account exists with that username/email, a password reset link has been sent.</p>
                        </div>
                    </div>
                </body>
                </html>
            `);
        }

        await VerificationToken.deleteMany({ userId: user._id, type: 'password_reset' });

        const confirmHash = generateConfirmHash();
        const token = new VerificationToken({
            userId: user._id,
            confirmHash,
            type: 'password_reset',
        });
        await token.save();

        console.log(`Password reset email would be sent to ${user.email} with link: /verify.php?id=${user._id}&confirm_hash=${confirmHash}`);

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Password Reset - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    .success { background: #d4edda; padding: 15px; border-radius: 5px; color: #155724; }
                    .info { margin-top: 15px; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Password Reset</h1>
                    <div class="success">
                        <p>Password reset request received.</p>
                        <p>A reset link has been sent to the email associated with this account.</p>
                    </div>
                    <div class="info">
                        <p>The link will expire in 5 minutes.</p>
                        <p>User ID: <strong>${user._id}</strong></p>
                    </div>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('Password reset error:', error);
        res.status(500).send('Password reset failed');
    }
});

app.get('/login', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - BugTracker</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                form { margin-top: 20px; }
                label { display: block; margin-top: 15px; font-weight: bold; }
                input { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
                button { margin-top: 20px; padding: 12px 30px; background: #0066cc; color: white; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #0052a3; }
                .links { margin-top: 15px; }
                .links a { color: #0066cc; display: block; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Login</h1>
                <form action="/login" method="post">
                    <label for="username">Username:</label>
                    <input type="text" name="username" id="username" required>
                    
                    <label for="password">Password:</label>
                    <input type="password" name="password" id="password" required>
                    
                    <button type="submit">Login</button>
                </form>
                <div class="links">
                    <a href="/signup">Create Account</a>
                    <a href="/lost_password">Forgot Password?</a>
                </div>
            </div>
        </body>
        </html>
    `);
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    
    try {
        const user = await User.findOne({ username });
        if (!user) {
            return res.redirect('/login?error=invalid');
        }
        
        if (!user.enabled) {
            return res.redirect('/login?error=disabled');
        }
        
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.redirect('/login?error=invalid');
        }
        
        req.session.userId = user._id;
        req.session.username = user.username;
        req.session.role = user.role;
        
        res.redirect('/my_view');
    } catch (error) {
        console.error('Login error:', error);
        res.redirect('/login?error=server');
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});

app.get('/my_view', requireAuth, async (req, res) => {
    try {
        const user = await User.findById(req.session.userId);
        const issues = await Issue.find({}).populate('reporter').limit(10);
        
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>My View - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1, h2 { color: #333; }
                    nav { margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #ddd; }
                    nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
                    nav a:hover { text-decoration: underline; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background: #f8f9fa; }
                    .user-info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <nav>
                        <a href="/my_view">My View</a>
                        <a href="/view_all">View Issues</a>
                        <a href="/account">My Account</a>
                        ${user.role === 'administrator' ? '<a href="/admin">Admin</a>' : ''}
                        <a href="/logout">Logout</a>
                    </nav>
                    <h1>My View</h1>
                    <div class="user-info">
                        <p>Welcome, <strong>${user.realname}</strong> (${user.username})</p>
                        <p>Role: ${user.role}</p>
                    </div>
                    <h2>Recent Issues</h2>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Reporter</th>
                        </tr>
                        ${issues.map(issue => `
                            <tr>
                                <td>${issue._id.toString().slice(-6)}</td>
                                <td>${issue.title}</td>
                                <td>${issue.status}</td>
                                <td>${issue.priority}</td>
                                <td>${issue.reporter ? issue.reporter.username : 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </table>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('My view error:', error);
        res.status(500).send('Error loading page');
    }
});

app.get('/view_all', requireAuth, async (req, res) => {
    try {
        const user = await User.findById(req.session.userId);
        const issues = await Issue.find({}).populate('reporter').populate('assignee');
        
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>All Issues - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    nav { margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #ddd; }
                    nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background: #f8f9fa; }
                </style>
            </head>
            <body>
                <div class="container">
                    <nav>
                        <a href="/my_view">My View</a>
                        <a href="/view_all">View Issues</a>
                        <a href="/account">My Account</a>
                        ${user.role === 'administrator' ? '<a href="/admin">Admin</a>' : ''}
                        <a href="/logout">Logout</a>
                    </nav>
                    <h1>All Issues</h1>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Priority</th>
                        </tr>
                        ${issues.map(issue => `
                            <tr>
                                <td>${issue._id.toString().slice(-6)}</td>
                                <td>${issue.title}</td>
                                <td>${issue.description}</td>
                                <td>${issue.status}</td>
                                <td>${issue.priority}</td>
                            </tr>
                        `).join('')}
                    </table>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('View all error:', error);
        res.status(500).send('Error loading page');
    }
});

app.get('/account', requireAuth, async (req, res) => {
    try {
        const user = await User.findById(req.session.userId);
        
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Account - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    nav { margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #ddd; }
                    nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
                    .info-row { padding: 10px 0; border-bottom: 1px solid #eee; }
                    .info-row label { font-weight: bold; display: inline-block; width: 120px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <nav>
                        <a href="/my_view">My View</a>
                        <a href="/view_all">View Issues</a>
                        <a href="/account">My Account</a>
                        ${user.role === 'administrator' ? '<a href="/admin">Admin</a>' : ''}
                        <a href="/logout">Logout</a>
                    </nav>
                    <h1>My Account</h1>
                    <div class="info-row">
                        <label>Username:</label> ${user.username}
                    </div>
                    <div class="info-row">
                        <label>Email:</label> ${user.email}
                    </div>
                    <div class="info-row">
                        <label>Real Name:</label> ${user.realname}
                    </div>
                    <div class="info-row">
                        <label>Role:</label> ${user.role}
                    </div>
                    <div class="info-row">
                        <label>Created:</label> ${user.createdAt.toISOString()}
                    </div>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('Account error:', error);
        res.status(500).send('Error loading page');
    }
});

app.get('/admin', requireAuth, async (req, res) => {
    try {
        const user = await User.findById(req.session.userId);
        
        if (user.role !== 'administrator') {
            return res.status(403).send('Access denied');
        }
        
        const users = await User.find({});
        const totalIssues = await Issue.countDocuments();
        
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Panel - BugTracker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    h1, h2 { color: #333; }
                    nav { margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #ddd; }
                    nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
                    .stats { background: #e7f3ff; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                    .flag-section { background: #fff3cd; padding: 20px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ffc107; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background: #f8f9fa; }
                </style>
            </head>
            <body>
                <div class="container">
                    <nav>
                        <a href="/my_view">My View</a>
                        <a href="/view_all">View Issues</a>
                        <a href="/account">My Account</a>
                        <a href="/admin">Admin</a>
                        <a href="/logout">Logout</a>
                    </nav>
                    <h1>Administration Panel</h1>
                    <div class="stats">
                        <h2>System Statistics</h2>
                        <p>Total Users: ${users.length}</p>
                        <p>Total Issues: ${totalIssues}</p>
                    </div>
                    <div class="flag-section">
                        <h2>System Configuration</h2>
                        <p>Secret Key: <code>${flag}</code></p>
                    </div>
                    <h2>User Management</h2>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Status</th>
                        </tr>
                        ${users.map(u => `
                            <tr>
                                <td>${u._id}</td>
                                <td>${u.username}</td>
                                <td>${u.email}</td>
                                <td>${u.role}</td>
                                <td>${u.enabled ? 'Enabled' : 'Disabled'}</td>
                            </tr>
                        `).join('')}
                    </table>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        console.error('Admin error:', error);
        res.status(500).send('Error loading page');
    }
});

app.get('/api/users', async (req, res) => {
    try {
        const users = await User.find({}, '_id username role createdAt');
        res.json(users);
    } catch (error) {
        res.status(500).json({ error: 'Server error' });
    }
});
