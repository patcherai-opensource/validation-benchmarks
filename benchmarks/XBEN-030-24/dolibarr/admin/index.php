<?php
/**
 * Dolibarr ERP & CRM - Admin Tools
 * Version 12.0.3
 */

session_start();

// Check if user is logged in and is admin
if (!isset($_SESSION['dolibarr_user']) || !isset($_SESSION['dolibarr_admin'])) {
    header('Location: /?error=access_denied');
    exit;
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Tools - Dolibarr ERP/CRM 12.0.3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header .version { font-size: 12px; color: #95a5a6; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover, .nav a.active { background: #2c3e50; border-radius: 3px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 25px; margin-bottom: 20px; }
        .card h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .admin-menu { list-style: none; }
        .admin-menu li { padding: 12px 15px; border-bottom: 1px solid #eee; }
        .admin-menu li:hover { background: #f8f9fa; }
        .admin-menu a { text-decoration: none; color: #2c3e50; display: flex; align-items: center; }
        .admin-menu a span { margin-right: 15px; font-size: 20px; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Dolibarr ERP/CRM</h1>
            <span class="version">Version 12.0.3</span>
        </div>
        <div>
            Welcome, <strong><?php echo htmlspecialchars($_SESSION['dolibarr_user']); ?></strong> |
            <a href="/?logout=1" style="color: #e74c3c;">Logout</a>
        </div>
    </div>

    <div class="nav">
        <a href="/">Home</a>
        <a href="/admin/" class="active">Admin Tools</a>
        <a href="/admin/tools/dolibarr_export.php">Backup</a>
    </div>

    <div class="container">
        <div class="card">
            <h2>Administration Tools</h2>
            <ul class="admin-menu">
                <li>
                    <a href="/admin/tools/dolibarr_export.php">
                        <span>💾</span>
                        Backup / Export Database & Files
                    </a>
                </li>
                <li>
                    <a href="#">
                        <span>📥</span>
                        Import / Restore
                    </a>
                </li>
                <li>
                    <a href="#">
                        <span>⚙️</span>
                        System Configuration
                    </a>
                </li>
                <li>
                    <a href="#">
                        <span>👥</span>
                        Users & Groups
                    </a>
                </li>
                <li>
                    <a href="#">
                        <span>📊</span>
                        System Information
                    </a>
                </li>
            </ul>
        </div>
    </div>

    <div class="footer">
        <p>Dolibarr ERP/CRM 12.0.3 - Open Source Software</p>
    </div>
</body>
</html>
