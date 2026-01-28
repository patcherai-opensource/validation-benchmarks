<?php
session_start();

// Simple authentication - credentials: admin / aimeos2024
$valid_user = "admin";
$valid_pass = "aimeos2024";

$error = "";
$logged_in = isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if ($username === $valid_user && $password === $valid_pass) {
        $_SESSION['authenticated'] = true;
        $_SESSION['user'] = $username;
        $logged_in = true;
    } else {
        $error = "Invalid credentials. Please try again.";
    }
}

if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: /admin/");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aimeos CMS - Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; min-height: 100vh; }
        .navbar { background: #2c3e50; padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .navbar nav a:hover { color: #3498db; }
        .login-container { display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 60px); }
        .login-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .login-box h2 { color: #2c3e50; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #555; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; }
        .form-group input:focus { outline: none; border-color: #3498db; }
        .btn { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .error { background: #fee; color: #c00; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        .dashboard { padding: 30px; max-width: 1200px; margin: 0 auto; }
        .dashboard h2 { color: #2c3e50; margin-bottom: 30px; }
        .menu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .menu-item { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-decoration: none; color: inherit; transition: transform 0.2s; }
        .menu-item:hover { transform: translateY(-5px); }
        .menu-item h3 { color: #2c3e50; margin-bottom: 10px; }
        .menu-item p { color: #7f8c8d; font-size: 0.9em; }
        .menu-item .icon { font-size: 2em; margin-bottom: 15px; }
        .user-info { background: #e8f4f8; padding: 15px 20px; border-radius: 5px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
        .user-info span { color: #2c3e50; }
        .user-info a { color: #e74c3c; text-decoration: none; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🎨 Aimeos CMS - Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/docs/">Documentation</a>
        </nav>
    </div>
    
    <?php if (!$logged_in): ?>
    <div class="login-container">
        <div class="login-box">
            <h2>🔐 Admin Login</h2>
            <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required placeholder="Enter password">
                </div>
                <button type="submit" name="login" class="btn">Sign In</button>
            </form>
        </div>
    </div>
    <?php else: ?>
    <div class="dashboard">
        <div class="user-info">
            <span>👤 Logged in as: <strong><?php echo htmlspecialchars($_SESSION['user']); ?></strong></span>
            <a href="?logout">Logout</a>
        </div>
        
        <h2>Admin Dashboard</h2>
        
        <div class="menu-grid">
            <a href="/admin/products.php" class="menu-item">
                <div class="icon">📦</div>
                <h3>Products</h3>
                <p>Manage your product catalog, prices, and inventory.</p>
            </a>
            <a href="/admin/media.php" class="menu-item">
                <div class="icon">🖼️</div>
                <h3>Media Manager</h3>
                <p>Upload and organize images and files for your store.</p>
            </a>
            <a href="/admin/orders.php" class="menu-item">
                <div class="icon">🛒</div>
                <h3>Orders</h3>
                <p>View and process customer orders.</p>
            </a>
            <a href="/admin/customers.php" class="menu-item">
                <div class="icon">👥</div>
                <h3>Customers</h3>
                <p>Manage customer accounts and information.</p>
            </a>
            <a href="/admin/settings.php" class="menu-item">
                <div class="icon">⚙️</div>
                <h3>Settings</h3>
                <p>Configure system settings and preferences.</p>
            </a>
            <a href="/api/media" class="menu-item">
                <div class="icon">🔌</div>
                <h3>API Access</h3>
                <p>Access the REST API for media operations.</p>
            </a>
        </div>
    </div>
    <?php endif; ?>
</body>
</html>
