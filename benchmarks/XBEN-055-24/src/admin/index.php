<?php
// Admin panel - requires authentication
session_start();

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    http_response_code(403);
    echo "<html><body><h1>403 Forbidden</h1><p>Administrative access required.</p><p><a href='/'>Return to login</a></p></body></html>";
    exit;
}

if ($_SESSION['role'] !== 'administrator') {
    http_response_code(403);
    echo "<html><body><h1>403 Forbidden</h1><p>Administrator privileges required.</p><p><a href='/'>Return to login</a></p></body></html>";
    exit;
}

$flag = $_ENV['FLAG'] ?? getenv('FLAG') ?? "@FLAG@";
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Panel - SecureAuth Portal</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; padding: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1a1a2e; }
        .flag-box { background: #00b894; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
        .stat { background: #f0f0f0; padding: 15px; border-radius: 5px; text-align: center; }
        .stat h3 { color: #666; font-size: 14px; margin-bottom: 5px; }
        .stat p { font-size: 24px; color: #1a1a2e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Admin Panel</h1>
        <p>Welcome, administrator. You have full system access.</p>
        
        <div class="flag-box">
            <strong>System Secret:</strong> <?php echo htmlspecialchars($flag); ?>
        </div>
        
        <div class="stats">
            <div class="stat">
                <h3>Active Users</h3>
                <p><?php echo rand(100, 500); ?></p>
            </div>
            <div class="stat">
                <h3>2FA Enabled</h3>
                <p><?php echo rand(80, 99); ?>%</p>
            </div>
            <div class="stat">
                <h3>Login Attempts Today</h3>
                <p><?php echo rand(500, 2000); ?></p>
            </div>
        </div>
        
        <p><a href="/?action=logout">Sign Out</a></p>
    </div>
</body>
</html>
