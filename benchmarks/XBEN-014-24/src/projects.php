<?php
/**
 * TaskFlow Portal - Projects Page
 */
session_start();

$authenticated_user = $_SESSION['user'] ?? null;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Projects - TaskFlow Portal</title>
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
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .nav-links a { color: #e0e0e0; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .login-required { text-align: center; color: #ff6666; padding: 50px; }
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
                <h2>Project Management</h2>
                <p style="margin-top: 15px; color: #888;">
                    Manage your assigned projects and track progress.
                </p>
                <ul style="margin-top: 20px; list-style: none;">
                    <li style="padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        📁 <strong>Demo Project</strong> - In Progress (65%)
                    </li>
                    <li style="padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        📁 <strong>Sample Tasks</strong> - Planning (15%)
                    </li>
                </ul>
            </div>
        <?php else: ?>
            <div class="card login-required">
                <h2>Authentication Required</h2>
                <p style="margin-top: 15px;">Please <a href="/" style="color: #00d4ff;">sign in</a> to view your projects.</p>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
