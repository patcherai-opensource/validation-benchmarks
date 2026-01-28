<?php
/**
 * Dolibar ERP - Admin Tools
 */

session_start();

// Check authentication
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: /admin/login.php");
    exit;
}

$username = htmlspecialchars($_SESSION['username']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolibar ERP - Admin Tools</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f6fa; }
        .header { background: #1a1a2e; color: #fff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 22px; }
        .header h1 span { color: #e94560; }
        .header .user-info { display: flex; align-items: center; gap: 15px; }
        .header .user-info a { color: #e94560; text-decoration: none; }
        .container { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #16213e; color: #fff; padding: 20px 0; }
        .sidebar h3 { padding: 10px 20px; color: #888; font-size: 12px; text-transform: uppercase; margin-bottom: 10px; }
        .sidebar ul { list-style: none; }
        .sidebar li a { display: block; padding: 12px 20px; color: #ccc; text-decoration: none; transition: background 0.2s; }
        .sidebar li a:hover, .sidebar li a.active { background: #1a1a2e; color: #fff; border-left: 3px solid #e94560; }
        .main { flex: 1; padding: 30px; }
        .page-title { margin-bottom: 20px; }
        .page-title h2 { color: #1a1a2e; margin-bottom: 5px; }
        .page-title p { color: #666; }
        .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .tool-card { background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .tool-card h3 { color: #1a1a2e; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
        .tool-card h3 .icon { font-size: 24px; }
        .tool-card p { color: #666; font-size: 14px; margin-bottom: 15px; }
        .tool-card a { display: inline-block; background: #e94560; color: #fff; padding: 10px 20px; border-radius: 4px; text-decoration: none; }
        .tool-card a:hover { background: #d63350; }
        .breadcrumb { margin-bottom: 20px; color: #666; }
        .breadcrumb a { color: #e94560; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Doli<span>bar</span> ERP</h1>
        <div class="user-info">
            <span>Welcome, <?php echo $username; ?></span>
            <a href="/admin/logout.php">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <nav class="sidebar">
            <h3>Main Menu</h3>
            <ul>
                <li><a href="/admin/index.php">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/products.php">Products</a></li>
                <li><a href="/admin/invoices.php">Invoices</a></li>
                <li><a href="/admin/reports.php">Reports</a></li>
            </ul>
            <h3>System</h3>
            <ul>
                <li><a href="/admin/users.php">Users</a></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/tools/" class="active">Admin Tools</a></li>
            </ul>
        </nav>
        
        <main class="main">
            <div class="breadcrumb">
                <a href="/admin/index.php">Dashboard</a> / Admin Tools
            </div>
            
            <div class="page-title">
                <h2>Administration Tools</h2>
                <p>System maintenance, backup, and data management utilities.</p>
            </div>
            
            <div class="tools-grid">
                <div class="tool-card">
                    <h3><span class="icon">📊</span> Database Export</h3>
                    <p>Export your database to SQL format for backup or migration purposes.</p>
                    <a href="dolibar_export.php">Export Database</a>
                </div>
                
                <div class="tool-card">
                    <h3><span class="icon">📁</span> File Backup</h3>
                    <p>Create compressed archives of system files and documents.</p>
                    <a href="export_files.php">Backup Files</a>
                </div>
                
                <div class="tool-card">
                    <h3><span class="icon">🔄</span> Import Data</h3>
                    <p>Import customers, products, or invoices from CSV files.</p>
                    <a href="import.php">Import Data</a>
                </div>
                
                <div class="tool-card">
                    <h3><span class="icon">📝</span> System Logs</h3>
                    <p>View application logs, access logs, and error reports.</p>
                    <a href="logs.php">View Logs</a>
                </div>
                
                <div class="tool-card">
                    <h3><span class="icon">🔧</span> Cache Management</h3>
                    <p>Clear application cache and regenerate static files.</p>
                    <a href="cache.php">Manage Cache</a>
                </div>
                
                <div class="tool-card">
                    <h3><span class="icon">📈</span> Performance</h3>
                    <p>View system performance metrics and optimize settings.</p>
                    <a href="performance.php">Performance</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
