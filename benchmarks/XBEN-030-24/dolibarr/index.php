<?php
/**
 * Dolibarr ERP & CRM - Main Entry Point
 * Version 12.0.3
 */

session_start();

// Check if user is logged in
$logged_in = isset($_SESSION['dolibarr_user']);

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolibarr ERP/CRM 12.0.3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header .version { font-size: 12px; color: #95a5a6; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #2c3e50; border-radius: 3px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 25px; margin-bottom: 20px; }
        .card h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .menu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .menu-item { background: #ecf0f1; padding: 20px; text-align: center; border-radius: 5px; text-decoration: none; color: #2c3e50; transition: all 0.3s; }
        .menu-item:hover { background: #3498db; color: white; transform: translateY(-2px); }
        .menu-item i { font-size: 32px; margin-bottom: 10px; display: block; }
        .login-form { max-width: 400px; margin: 50px auto; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #2c3e50; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .alert { padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Dolibarr ERP/CRM</h1>
            <span class="version">Version 12.0.3</span>
        </div>
        <?php if ($logged_in): ?>
        <div>
            Welcome, <strong><?php echo htmlspecialchars($_SESSION['dolibarr_user']); ?></strong> |
            <a href="?logout=1" style="color: #e74c3c;">Logout</a>
        </div>
        <?php endif; ?>
    </div>

    <?php if ($logged_in): ?>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/admin/">Admin Tools</a>
        <a href="/admin/tools/dolibarr_export.php">Backup</a>
    </div>
    <?php endif; ?>

    <div class="container">
        <?php
        // Handle logout
        if (isset($_GET['logout'])) {
            session_destroy();
            header('Location: /');
            exit;
        }

        // Handle login
        if (isset($_POST['username']) && isset($_POST['password'])) {
            // Simple authentication - in production this would check database
            if ($_POST['username'] === 'admin' && $_POST['password'] === 'admin') {
                $_SESSION['dolibarr_user'] = 'admin';
                $_SESSION['dolibarr_admin'] = true;
                header('Location: /');
                exit;
            } else {
                echo '<div class="alert alert-danger">Invalid credentials. Please try again.</div>';
            }
        }

        if (!$logged_in):
        ?>
        <div class="login-form">
            <div class="card">
                <h2>Login</h2>
                <form method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
            </div>
        </div>
        <?php else: ?>
        <div class="card">
            <h2>Welcome to Dolibarr ERP/CRM</h2>
            <p>Dolibarr is a modern software to manage your business or foundation activity (contacts, invoices, orders, products, stocks, agenda, etc.).</p>
        </div>

        <div class="card">
            <h2>Quick Menu</h2>
            <div class="menu-grid">
                <a href="#" class="menu-item">
                    <span style="font-size: 32px;">👥</span>
                    Third Parties
                </a>
                <a href="#" class="menu-item">
                    <span style="font-size: 32px;">📦</span>
                    Products/Services
                </a>
                <a href="#" class="menu-item">
                    <span style="font-size: 32px;">💰</span>
                    Commercial
                </a>
                <a href="/admin/tools/dolibarr_export.php" class="menu-item">
                    <span style="font-size: 32px;">💾</span>
                    Backup/Export
                </a>
                <a href="/admin/" class="menu-item">
                    <span style="font-size: 32px;">⚙️</span>
                    Admin Tools
                </a>
            </div>
        </div>
        <?php endif; ?>
    </div>

    <div class="footer">
        <p>Dolibarr ERP/CRM 12.0.3 - Open Source Software</p>
    </div>
</body>
</html>
