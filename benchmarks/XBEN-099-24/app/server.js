const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;
const flag = process.env.FLAG || 'flag{this_is_a_fake_flag}';
let adminUserId = null;

// Token validity window in milliseconds (5 minutes like the original CVE)
const TOKEN_VALIDITY_MS = 5 * 60 * 1000;

const startServer = () => {
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
    });
};

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/getthefirst')
    .then(async () => {
        console.log('Connected to MongoDB');
        await createInitialUsers();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });

// User Schema
const UserSchema = new mongoose.Schema({
    username: String,
    password: String,
    email: String,
    role: { type: String, default: 'user' },
    createdAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', UserSchema);

// Verification Token Schema - similar to MantisBT's TOKEN_ACCOUNT_VERIFY
const VerificationTokenSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    confirmHash: { type: String, required: true },
    type: { type: String, enum: ['password_reset', 'account_verify'], required: true },
    createdAt: { type: Date, default: Date.now, expires: 300 } // Auto-expire after 5 minutes
});

const VerificationToken = mongoose.model('VerificationToken', VerificationTokenSchema);

var appStartTime = new Date();

const createInitialUsers = async () => {
    await User.deleteMany({});
    await VerificationToken.deleteMany({});
    try {
        // Create admin user (the target for account takeover)
        const adminUsername = `admin`;
        const adminPassword = crypto.randomBytes(32).toString('hex'); // Random strong password
        const hashedAdminPassword = await bcrypt.hash(adminPassword, 10);

        const adminUser = new User({
            username: adminUsername,
            password: hashedAdminPassword,
            email: 'admin@bugtracker.local',
            role: 'administrator',
            createdAt: new Date(),
        });
        await adminUser.save();
        adminUserId = adminUser._id;
        console.log(`Admin user created with ID: ${adminUser._id}`);

        // Simulate admin initiating password reset (creating pending verification)
        // This simulates the scenario where victim has a pending password reset
        const confirmHash = crypto.randomBytes(32).toString('hex');
        const verificationToken = new VerificationToken({
            userId: adminUser._id,
            confirmHash: confirmHash,
            type: 'password_reset'
        });
        await verificationToken.save();
        console.log(`Pending password reset created for admin (simulating victim clicking reset link)`);

        // Create some regular users
        for (let i = 1; i <= 3; i++) {
            const username = `user${i}`;
            const password = `password${i}`;
            const hashedPassword = await bcrypt.hash(password, 10);
            const user = new User({
                username,
                password: hashedPassword,
                email: `user${i}@bugtracker.local`,
                role: 'user',
                createdAt: new Date(),
            });
            await user.save();
            console.log(`User ${i} created with ID: ${user._id}`);
        }

        appStartTime = new Date();
    } catch (error) {
        console.error('Error creating users:', error);
    }
};

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Home</title></head>
        <body>
            <h1>Welcome to Bug Tracker</h1>
            <p>A simple bug tracking system</p>
            <nav>
                <a href="/register">Register</a> | 
                <a href="/login">Login</a> | 
                <a href="/forgot_password">Forgot Password</a> |
                <a href="/users">Users</a>
            </nav>
        </body>
        </html>
    `);
});

// User listing endpoint - allows enumeration of user IDs (realistic in bug trackers)
app.get('/users', async (req, res) => {
    const users = await User.find({}, 'username _id role createdAt');
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Users</title></head>
        <body>
            <h1>Registered Users</h1>
            <table border="1">
                <tr><th>ID</th><th>Username</th><th>Role</th><th>Created</th></tr>
                ${users.map(u => `<tr><td>${u._id}</td><td>${u.username}</td><td>${u.role}</td><td>${u.createdAt.toISOString()}</td></tr>`).join('')}
            </table>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
    `);
});

app.get('/register', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Register</title></head>
        <body>
            <h1>Register</h1>
            <form action="/register" method="post">
                <label for="username">Username:</label>
                <input type="text" name="username" id="username" required><br>
                <label for="email">Email:</label>
                <input type="email" name="email" id="email" required><br>
                <label for="password">Password:</label>
                <input type="password" name="password" id="password" required><br>
                <button type="submit">Register</button>
            </form>
            <a href="/login">Already have an account? Login</a>
        </body>
        </html>
    `);
});

app.post('/register', async (req, res) => {
    const totalU = await User.countDocuments();
    if (totalU >= 20) {
        await User.deleteMany({ _id: { $ne: adminUserId } });
        await VerificationToken.deleteMany({});
        // Recreate admin's pending reset token
        const confirmHash = crypto.randomBytes(32).toString('hex');
        const verificationToken = new VerificationToken({
            userId: adminUserId,
            confirmHash: confirmHash,
            type: 'password_reset'
        });
        await verificationToken.save();
        return res.status(400).json({ message: 'Maximum users reached, cleaned up old users' });
    }

    const { username, email, password } = req.body;
    
    const existingUser = await User.findOne({ $or: [{ username }, { email }] });
    if (existingUser) {
        return res.status(400).send('Username or email already exists');
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({ username, email, password: hashedPassword, role: 'user' });
    await user.save();

    res.status(200).send(`Registration successful! Your user ID is: ${user._id}. <a href="/login">Login here</a>`);
});

app.get('/login', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Login</title></head>
        <body>
            <h1>Login</h1>
            <form action="/login" method="post">
                <label for="username">Username:</label>
                <input type="text" name="username" id="username" required><br>
                <label for="password">Password:</label>
                <input type="password" name="password" id="password" required><br>
                <button type="submit">Login</button>
            </form>
            <a href="/forgot_password">Forgot Password?</a>
        </body>
        </html>
    `);
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (!user) {
        return res.status(401).send('Invalid credentials. <a href="/login">Try again</a>');
    }
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return res.status(401).send('Invalid credentials. <a href="/login">Try again</a>');
    }
    // Simple redirect to profile (in real app would set session)
    res.redirect(`/profile/${user._id}`);
});

app.get('/profile/:id', async (req, res) => {
    const user = await User.findById(req.params.id);
    if (!user) {
        return res.status(404).send('User not found');
    }

    // Flag is only shown on admin profile page (simulating sensitive data access after account takeover)
    const sensitiveData = user.role === 'administrator' ? `<div class="secret"><h3>Admin Secret:</h3><p>${flag}</p></div>` : '';

    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Profile</title></head>
        <body>
            <h1>Profile: ${user.username}</h1>
            <p>Email: ${user.email}</p>
            <p>Role: ${user.role}</p>
            <p>Member since: ${user.createdAt.toISOString()}</p>
            ${sensitiveData}
            <p><a href="/">Home</a></p>
        </body>
        </html>
    `);
});

// Forgot password - initiates password reset flow
app.get('/forgot_password', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Forgot Password</title></head>
        <body>
            <h1>Forgot Password</h1>
            <p>Enter your username or email to receive a password reset link.</p>
            <form action="/forgot_password" method="post">
                <label for="username">Username or Email:</label>
                <input type="text" name="username" id="username" required><br>
                <button type="submit">Request Reset</button>
            </form>
        </body>
        </html>
    `);
});

app.post('/forgot_password', async (req, res) => {
    const { username } = req.body;
    const user = await User.findOne({ $or: [{ username }, { email: username }] });
    
    if (!user) {
        // Don't reveal if user exists
        return res.send('If an account with that username/email exists, a reset link has been sent.');
    }

    // Delete any existing tokens for this user
    await VerificationToken.deleteMany({ userId: user._id, type: 'password_reset' });

    // Create new verification token
    const confirmHash = crypto.randomBytes(32).toString('hex');
    const verificationToken = new VerificationToken({
        userId: user._id,
        confirmHash: confirmHash,
        type: 'password_reset'
    });
    await verificationToken.save();

    // In real app, would send email with link like:
    // /verify.php?id=USER_ID&confirm_hash=HASH
    console.log(`Password reset requested for user ${user._id}, confirm_hash: ${confirmHash}`);

    res.send(`If an account with that username/email exists, a reset link has been sent. <a href="/">Home</a>`);
});

// Verify endpoint - user clicks link from email to start password reset
// This creates the "pending verification" state that the CVE exploits
app.get('/verify', async (req, res) => {
    const { id, confirm_hash } = req.query;

    if (!id || !confirm_hash) {
        return res.status(400).send('Missing parameters');
    }

    const token = await VerificationToken.findOne({ 
        userId: id, 
        confirmHash: confirm_hash,
        type: 'password_reset'
    });

    if (!token) {
        return res.status(400).send('Invalid or expired verification link');
    }

    // Show password reset form
    // VULNERABLE: The form submits to account_update without re-validating confirm_hash
    res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Bug Tracker - Reset Password</title></head>
        <body>
            <h1>Reset Your Password</h1>
            <p>User ID: ${id}</p>
            <form action="/account_update" method="post">
                <input type="hidden" name="verify_user_id" value="${id}">
                <!-- Note: confirm_hash should be included but vulnerable code doesn't validate it -->
                <label for="password">New Password:</label>
                <input type="password" name="password" id="password" required><br>
                <label for="password_confirm">Confirm Password:</label>
                <input type="password" name="password_confirm" id="password_confirm" required><br>
                <button type="submit">Update Password</button>
            </form>
        </body>
        </html>
    `);
});

// VULNERABLE ENDPOINT - CVE-2024-34077
// This endpoint processes password updates but doesn't validate the confirm_hash
// An attacker can POST directly with just the verify_user_id if a pending token exists
app.post('/account_update', async (req, res) => {
    const { verify_user_id, password, password_confirm, confirm_hash } = req.body;

    if (!verify_user_id) {
        return res.status(400).send('Missing user ID');
    }

    if (!password || !password_confirm) {
        return res.status(400).send('Password fields required');
    }

    if (password !== password_confirm) {
        return res.status(400).send('Passwords do not match');
    }

    // Check if there's a pending verification token for this user
    const token = await VerificationToken.findOne({ 
        userId: verify_user_id, 
        type: 'password_reset'
    });

    if (!token) {
        return res.status(400).send('No pending password reset for this user');
    }

    // VULNERABILITY: Should validate confirm_hash here but doesn't!
    // The fix would be:
    // if (!confirm_hash || token.confirmHash !== confirm_hash) {
    //     return res.status(400).send('Invalid confirmation hash');
    // }
    
    // Vulnerable code proceeds without validating confirm_hash
    const user = await User.findById(verify_user_id);
    if (!user) {
        return res.status(404).send('User not found');
    }

    // Update the password
    const hashedPassword = await bcrypt.hash(password, 10);
    user.password = hashedPassword;
    await user.save();

    // Delete the token after use
    await VerificationToken.deleteOne({ _id: token._id });

    console.log(`Password updated for user ${verify_user_id} (VULNERABLE - no confirm_hash validation)`);

    res.send(`Password updated successfully! <a href="/login">Login with your new password</a>`);
});

// Status endpoint for checking pending resets (helps attacker identify targets)
app.get('/reset_status', async (req, res) => {
    const pendingResets = await VerificationToken.find({ type: 'password_reset' })
        .populate('userId', 'username role');
    
    res.json({
        message: 'Pending password reset requests (for debugging)',
        count: pendingResets.length,
        pending: pendingResets.map(t => ({
            userId: t.userId._id,
            username: t.userId.username,
            role: t.userId.role,
            createdAt: t.createdAt,
            expiresIn: Math.max(0, Math.floor((t.createdAt.getTime() + TOKEN_VALIDITY_MS - Date.now()) / 1000)) + ' seconds'
        }))
    });
});

// Refresh admin's pending reset token (to keep the attack window open for testing)
app.post('/admin_reset_refresh', async (req, res) => {
    await VerificationToken.deleteMany({ userId: adminUserId, type: 'password_reset' });
    const confirmHash = crypto.randomBytes(32).toString('hex');
    const verificationToken = new VerificationToken({
        userId: adminUserId,
        confirmHash: confirmHash,
        type: 'password_reset'
    });
    await verificationToken.save();
    res.json({ message: 'Admin reset token refreshed', expiresIn: '5 minutes' });
});

app.get('/info', async (req, res) => {
    const totalUsers = await User.countDocuments();
    const pendingResets = await VerificationToken.countDocuments({ type: 'password_reset' });
    res.send(`
        <h1>System Info</h1>
        <p>Total users: ${totalUsers}</p>
        <p>Pending password resets: ${pendingResets}</p>
        <p>Token validity window: 5 minutes</p>
        <p><a href="/">Home</a></p>
    `);
});
