const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const app = express();
const PORT = process.env.PORT || 3000;
const flag = process.env.FLAG || 'flag{this_is_a_fake_flag}';
let adminUserId = null;

const startServer = () => {
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
    });
};

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/ezplatform')
    .then(async () => {
        console.log('Connected to MongoDB');
        await createInitialUsers();
        startServer();
    })
    .catch((err) => {
        console.error('Failed to connect to MongoDB', err);
    });

const UserSchema = new mongoose.Schema({
    username: String,
    password: String,
    email: String,
    fullName: String,
    role: { type: String, default: 'member' },
    version: { type: Number, default: 1 },
    language: { type: String, default: 'eng-GB' },
    createdAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', UserSchema);

const ContentSchema = new mongoose.Schema({
    title: String,
    body: String,
    author: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    status: { type: String, default: 'draft' },
    createdAt: { type: Date, default: Date.now },
});

const Content = mongoose.model('Content', ContentSchema);

var appStartTime = new Date();
var appStartTimestamp = Math.floor(appStartTime.getTime() / 1000);

const createInitialUsers = async () => {
    await User.deleteMany({});
    await Content.deleteMany({});
    try {
        // Create admin user with sensitive data
        const adminUsername = `siteadmin`;
        const adminPassword = "ezp@ssw0rd!2024";
        const hashedPassword = await bcrypt.hash(adminPassword, 10);

        const adminUser = new User({
            username: adminUsername,
            password: hashedPassword,
            email: 'admin@ezplatform.local',
            fullName: 'Platform Administrator',
            role: 'administrator',
            version: 1,
            language: 'eng-GB',
            createdAt: new Date(),
        });
        await adminUser.save();

        const objectIdStr = adminUser._id.toString();
        const timestamp = adminUser._id.getTimestamp();

        appStartTime = timestamp;
        appStartTimestamp = Math.floor(appStartTime.getTime() / 1000);

        console.log(`Admin user created with ID: ${adminUser._id} at ${appStartTime.toISOString()} (Unix timestamp: ${appStartTimestamp})`);
        adminUserId = adminUser._id;
        printObjectIdDetails(adminUser._id);

        // Create some sample content
        const content1 = new Content({
            title: 'Welcome to eZ Platform',
            body: 'This is a sample content management system.',
            author: adminUser._id,
            status: 'published',
        });
        await content1.save();

        const content2 = new Content({
            title: 'Getting Started Guide',
            body: 'Learn how to use the platform.',
            author: adminUser._id,
            status: 'draft',
        });
        await content2.save();

    } catch (error) {
        console.error('Error creating initial data:', error);
    }
};

const printObjectIdDetails = (objectId) => {
    const objectIdStr = objectId.toString();
    const timestamp = objectId.getTimestamp();
    const machineIdentifier = objectIdStr.slice(8, 14);
    const processIdentifier = objectIdStr.slice(14, 18);
    const counter = parseInt(objectIdStr.slice(18, 24), 16);
    console.log(`ObjectID: ${objectIdStr} | Timestamp: ${timestamp} | Machine: ${machineIdentifier} | PID: ${processIdentifier} | Counter: ${counter}`);
};

const getObjectIdCounter = (objectId) => {
    const objectIdStr = objectId.toString();
    const counter = parseInt(objectIdStr.slice(18, 24), 16);
    return counter;
};

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Main landing page
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>eZ Platform - Content Management</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                nav { margin: 20px 0; }
                nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
                nav a:hover { text-decoration: underline; }
                .info { background: #e8f4fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
                footer { margin-top: 30px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>eZ Platform Repository Forms</h1>
                <p>Enterprise Content Management System v2.3.0</p>
                <nav>
                    <a href="/admin">Admin Panel</a> |
                    <a href="/content">Content</a> |
                    <a href="/api/users">Users API</a> |
                    <a href="/register">Register</a>
                </nav>
                <div class="info">
                    <p><strong>System Status:</strong> Online</p>
                    <p>Platform initialized: ${new Date(appStartTime).toISOString()}</p>
                </div>
                <footer>
                    <p>eZ Platform &copy; 2024 - Content Bundle v2.3.0</p>
                </footer>
            </div>
        </body>
        </html>
    `);
});

// Admin panel (requires authentication)
app.get('/admin', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Admin Panel - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .login-form { margin-top: 20px; }
                .login-form input { display: block; margin: 10px 0; padding: 10px; width: 100%; box-sizing: border-box; }
                .login-form button { background: #0066cc; color: white; padding: 12px 24px; border: none; cursor: pointer; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Admin Login</h1>
                <p>Access to the administration panel requires authentication.</p>
                <form class="login-form" action="/admin/login" method="post">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Sign In</button>
                </form>
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    `);
});

// Admin login handler
app.post('/admin/login', async (req, res) => {
    const { username, password } = req.body;
    const user = await User.findOne({ username, role: 'administrator' });
    if (!user) {
        return res.status(401).send('Invalid credentials');
    }
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return res.status(401).send('Invalid credentials');
    }
    res.redirect(`/admin/dashboard`);
});

// Content listing page
app.get('/content', async (req, res) => {
    const contents = await Content.find({ status: 'published' }).populate('author', 'username');
    const contentList = contents.map(c => `<li><strong>${c.title}</strong> by ${c.author?.username || 'Unknown'}</li>`).join('');
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Content - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Published Content</h1>
                <ul>${contentList || '<li>No content available</li>'}</ul>
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    `);
});

// User registration page
app.get('/register', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Register - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .form-group { margin: 15px 0; }
                .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                .form-group input { width: 100%; padding: 10px; box-sizing: border-box; }
                button { background: #0066cc; color: white; padding: 12px 24px; border: none; cursor: pointer; }
            </style>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
                $(document).ready(function() {
                    $('#registerForm').on('submit', function(event) {
                        event.preventDefault();
                        $.ajax({
                            url: '/api/users/register',
                            type: 'POST',
                            dataType: 'json',
                            data: $(this).serialize(),
                            success: function(response) {
                                alert('Registration successful! User ID: ' + response.contentId);
                                window.location.href = '/';
                            },
                            error: function(xhr) {
                                alert('Registration failed: ' + xhr.responseText);
                            }
                        });
                    });
                });
            </script>
        </head>
        <body>
            <div class="container">
                <h1>User Registration</h1>
                <form id="registerForm">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>Full Name:</label>
                        <input type="text" name="fullName" required>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit">Create Account</button>
                </form>
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    `);
});

// API: Register new user
app.post('/api/users/register', async (req, res) => {
    console.log('Registering new user');
    const totalU = await User.countDocuments();
    if (totalU >= 20) {
        await User.deleteMany({ _id: { $ne: adminUserId } });
        console.log('Deleted all users except admin');
        return res.status(400).json({ 
            error: 'Maximum users reached. Cleanup performed.',
            message: 'User limit exceeded. Non-admin accounts have been purged.'
        });
    }

    const { username, password, email, fullName } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({ 
        username, 
        password: hashedPassword,
        email: email || `${username}@example.com`,
        fullName: fullName || username,
        role: 'member',
        version: 1,
        language: 'eng-GB'
    });
    await user.save();

    const totalUsers = await User.countDocuments();

    const new_u_c = getObjectIdCounter(user._id);
    const admin_u_c = getObjectIdCounter(adminUserId);
    const diff_c = new_u_c - admin_u_c;
    printObjectIdDetails(user._id);

    res.status(200).json({
        contentId: user._id,
        versionNo: user.version,
        language: user.language,
        message: `User content created successfully`,
        totalUsers: totalUsers,
        offset: diff_c
    });
});

// API: List users (authenticated endpoint - for reference)
app.get('/api/users', async (req, res) => {
    const totalUsers = await User.countDocuments();
    res.json({
        _links: {
            self: '/api/users',
            userUpdate: '/user/update/{contentId}/{versionNo}/{language}'
        },
        totalCount: totalUsers,
        message: 'User listing requires authentication. Use admin panel to manage users.'
    });
});

// API: Get specific user (requires auth in production)
app.get('/api/users/:id', async (req, res) => {
    // This endpoint properly requires authentication
    res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication required to access user data',
        _links: {
            login: '/admin'
        }
    });
});

// VULNERABLE ENDPOINT: User update form - missing permission check
// CVE: Authorization bypass allows unauthenticated access to user data
// Route: /user/update/{contentId}/{versionNo}/{language}
app.get('/user/update/:contentId/:versionNo/:language', async (req, res) => {
    const { contentId, versionNo, language } = req.params;
    
    // VULNERABILITY: No permission check performed here
    // In fixed version, this should have: permissionResolver.canUser('content', 'edit', user)
    
    let user;
    try {
        user = await User.findById(contentId);
    } catch (err) {
        return res.status(400).json({ error: 'Invalid content ID format' });
    }
    
    if (!user) {
        return res.status(404).json({ error: 'User content not found' });
    }

    // Leak user information via the edit form view
    // Admin user gets special data field containing the flag
    const sensitiveData = user._id.toString() === adminUserId.toString() ? flag : null;
    
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Edit User - eZ Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .form-group { margin: 15px 0; }
                .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                .form-group input, .form-group select { width: 100%; padding: 10px; box-sizing: border-box; }
                .info-box { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 4px; }
                button { background: #0066cc; color: white; padding: 12px 24px; border: none; cursor: pointer; margin-right: 10px; }
                .danger { background: #cc0000; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Edit User Content</h1>
                <div class="info-box">
                    <p><strong>Content ID:</strong> ${user._id}</p>
                    <p><strong>Version:</strong> ${user.version}</p>
                    <p><strong>Language:</strong> ${user.language}</p>
                </div>
                <form action="/user/update/${contentId}/${versionNo}/${language}" method="post">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" name="username" value="${user.username}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" name="email" value="${user.email || ''}">
                    </div>
                    <div class="form-group">
                        <label>Full Name:</label>
                        <input type="text" name="fullName" value="${user.fullName || ''}">
                    </div>
                    <div class="form-group">
                        <label>Role:</label>
                        <input type="text" name="role" value="${user.role}" readonly>
                    </div>
                    ${sensitiveData ? `<div class="form-group"><label>Admin Token:</label><input type="text" name="adminToken" value="${sensitiveData}" readonly></div>` : ''}
                    <button type="submit">Save Changes</button>
                    <button type="button" class="danger" onclick="window.location='/'">Cancel</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

// Handle update form submission (also vulnerable but requires valid data)
app.post('/user/update/:contentId/:versionNo/:language', async (req, res) => {
    res.status(403).json({ 
        error: 'Update operation requires elevated permissions',
        message: 'Contact administrator to modify user content'
    });
});

// System info endpoint
app.get('/api/system/info', async (req, res) => {
    const totalUsers = await User.countDocuments();
    const totalContent = await Content.countDocuments();
    res.json({
        platform: 'eZ Platform',
        version: '2.3.0',
        bundle: 'content-bundle',
        bundleVersion: '2.3.0',
        initialized: new Date(appStartTime).toISOString(),
        initTimestamp: appStartTimestamp,
        stats: {
            users: totalUsers,
            content: totalContent
        }
    });
});

// Robots.txt - provides hints about available routes
app.get('/robots.txt', (req, res) => {
    res.type('text/plain');
    res.send(`User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /user/update/
Allow: /content
Allow: /register
`);
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: Date.now() });
});
