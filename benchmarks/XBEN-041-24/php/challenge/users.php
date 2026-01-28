<?php
session_start();
$is_admin = isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
?>
<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Users</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5em; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .header nav a:hover { text-decoration: underline; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .panel { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .panel h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; color: #2c3e50; }
        .role-admin { color: #e74c3c; font-weight: 600; }
        .role-editor { color: #3498db; font-weight: 600; }
        .role-viewer { color: #27ae60; font-weight: 600; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }
        .alert { padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; margin-bottom: 20px; color: #721c24; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📁 MediaFlow CMS</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/pages.php">Pages</a>
            <a href="/admin/media.php">Media</a>
            <a href="/settings.php">Settings</a>
            <a href="/docs.php">Documentation</a>
        </nav>
    </div>
    <div class="container">
        <?php if (!$is_admin): ?>
            <div class="alert">🔒 You need admin access to manage users. <a href="/admin/media.php">Login here</a></div>
        <?php endif; ?>
        
        <div class="panel">
            <h2>👥 User Management</h2>
            <table>
                <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Last Login</th>
                </tr>
                <tr>
                    <td>admin</td>
                    <td>admin@mediaflow.local</td>
                    <td class="role-admin">Administrator</td>
                    <td>2024-01-20 14:32</td>
                </tr>
                <tr>
                    <td>editor1</td>
                    <td>editor@mediaflow.local</td>
                    <td class="role-editor">Editor</td>
                    <td>2024-01-19 09:15</td>
                </tr>
                <tr>
                    <td>viewer</td>
                    <td>viewer@mediaflow.local</td>
                    <td class="role-viewer">Viewer</td>
                    <td>2024-01-18 16:45</td>
                </tr>
            </table>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
