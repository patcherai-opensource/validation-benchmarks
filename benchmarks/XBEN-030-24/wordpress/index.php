<?php
/**
 * PluginCrate - Plugin Management System
 * A lightweight plugin management interface for your applications
 */

session_start();

// Admin credentials - default installation
$ADMIN_USER = 'admin';
$ADMIN_PASS = 'plugin_admin_2024';

// Handle logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header('Location: /');
    exit;
}

// Check authentication
$authenticated = isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    if ($_POST['username'] === $ADMIN_USER && $_POST['password'] === $ADMIN_PASS) {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $ADMIN_USER;
        header('Location: /admin');
        exit;
    } else {
        $login_error = "Invalid credentials";
    }
}

// Routing
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($path === '/admin' && !$authenticated) {
    header('Location: /login');
    exit;
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PluginCrate - Plugin Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 {
            color: #4fc3f7;
            font-size: 1.8rem;
        }
        header nav a {
            color: #4fc3f7;
            text-decoration: none;
            margin-left: 20px;
        }
        .card {
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .card h2 {
            color: #4fc3f7;
            margin-bottom: 15px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #b0b0b0;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #333;
            border-radius: 5px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1rem;
        }
        .btn {
            background: #4fc3f7;
            color: #000;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
        }
        .btn:hover {
            background: #29b6f6;
        }
        .plugin-list {
            list-style: none;
        }
        .plugin-list li {
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .plugin-status {
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.8rem;
        }
        .status-active {
            background: #4caf50;
            color: #fff;
        }
        .status-inactive {
            background: #ff9800;
            color: #000;
        }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
        }
        .error {
            background: #f44336;
            color: #fff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .success {
            background: #4caf50;
            color: #fff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .hero {
            text-align: center;
            padding: 60px 20px;
        }
        .hero h2 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: #4fc3f7;
        }
        .hero p {
            font-size: 1.2rem;
            color: #b0b0b0;
            max-width: 600px;
            margin: 0 auto 30px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .feature {
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }
        .feature h3 {
            color: #4fc3f7;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <?php if ($path === '/login'): ?>
            <!-- Login Page -->
            <div class="login-container">
                <div class="card">
                    <h2>Administrator Login</h2>
                    <?php if (isset($login_error)): ?>
                        <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
                    <?php endif; ?>
                    <form method="POST" action="/login">
                        <div class="form-group">
                            <label>Username</label>
                            <input type="text" name="username" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" name="password" required>
                        </div>
                        <button type="submit" name="login" class="btn">Sign In</button>
                    </form>
                </div>
                <p style="text-align: center; margin-top: 20px; color: #666;">
                    <a href="/" style="color: #4fc3f7;">← Back to Home</a>
                </p>
            </div>
        
        <?php elseif ($path === '/admin' && $authenticated): ?>
            <!-- Admin Dashboard -->
            <header>
                <h1>🔌 PluginCrate Admin</h1>
                <nav>
                    <span>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?></span>
                    <a href="/?action=logout">Logout</a>
                </nav>
            </header>
            
            <?php include 'admin.php'; ?>
            
        <?php else: ?>
            <!-- Public Home Page -->
            <header>
                <h1>🔌 PluginCrate</h1>
                <nav>
                    <a href="/">Home</a>
                    <a href="/login">Admin Login</a>
                </nav>
            </header>
            
            <div class="hero">
                <h2>Modern Plugin Management</h2>
                <p>PluginCrate is a powerful plugin management system that lets you install, configure, and manage plugins from various sources including NPM and Git repositories.</p>
                <a href="/login" class="btn">Admin Access →</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>📦 NPM Integration</h3>
                    <p>Install plugins directly from the NPM registry with a single click.</p>
                </div>
                <div class="feature">
                    <h3>🔗 Git Repositories</h3>
                    <p>Clone and install plugins from any Git repository URL.</p>
                </div>
                <div class="feature">
                    <h3>⚙️ Easy Configuration</h3>
                    <p>Configure plugins through an intuitive admin interface.</p>
                </div>
            </div>
            
            <!-- TODO: Remove default credentials before production deployment -->
            <!-- Admin: admin / plugin_admin_2024 -->
        <?php endif; ?>
    </div>
</body>
</html>
