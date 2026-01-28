<?php
/**
 * TaskFlow Portal - Settings Page
 */
session_start();

$authenticated_user = $_SESSION['user'] ?? null;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Settings - TaskFlow Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .nav-links a { color: #e0e0e0; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .setting-item { padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .setting-item:last-child { border: none; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">📊 TaskFlow Portal</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/projects.php">Projects</a>
            <a href="/team.php">Team</a>
            <a href="/settings.php">Settings</a>
        </div>
    </nav>
    <div class="container">
        <?php if ($authenticated_user): ?>
            <div class="card">
                <h2>Account Settings</h2>
                <div class="setting-item">
                    <strong>Username:</strong> <?php echo htmlspecialchars($authenticated_user); ?>
                </div>
                <div class="setting-item">
                    <strong>Session Type:</strong> <?php echo isset($_COOKIE['remember_session']) ? 'Persistent (Remember Me)' : 'Standard Session'; ?>
                </div>
                <div class="setting-item">
                    <strong>Session ID:</strong> <code><?php echo session_id(); ?></code>
                </div>
            </div>
            <div class="card">
                <h2>Security Settings</h2>
                <div class="setting-item">
                    <strong>Two-Factor Authentication:</strong> Disabled
                </div>
                <div class="setting-item">
                    <strong>Active Sessions:</strong> 1
                </div>
            </div>
        <?php else: ?>
            <div class="card" style="text-align: center;">
                <h2>Authentication Required</h2>
                <p style="margin-top: 15px;">Please <a href="/" style="color: #00d4ff;">sign in</a> to access settings.</p>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
