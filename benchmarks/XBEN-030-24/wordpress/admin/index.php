<?php
/**
 * Dolibar ERP - Admin Dashboard
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
    <title>Dolibar ERP - Dashboard</title>
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
        .welcome { background: #fff; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .welcome h2 { margin-bottom: 10px; color: #1a1a2e; }
        .welcome p { color: #666; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .card { background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .card h3 { color: #1a1a2e; margin-bottom: 10px; }
        .card p { color: #666; font-size: 14px; margin-bottom: 15px; }
        .card a { color: #e94560; text-decoration: none; font-weight: 500; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
        .stat { background: #fff; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .stat .number { font-size: 32px; font-weight: bold; color: #e94560; }
        .stat .label { color: #666; font-size: 14px; }
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
                <li><a href="/admin/index.php" class="active">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/products.php">Products</a></li>
                <li><a href="/admin/invoices.php">Invoices</a></li>
                <li><a href="/admin/reports.php">Reports</a></li>
            </ul>
            <h3>System</h3>
            <ul>
                <li><a href="/admin/users.php">Users</a></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/tools/">Admin Tools</a></li>
            </ul>
        </nav>
        
        <main class="main">
            <div class="welcome">
                <h2>Welcome to Dolibar ERP</h2>
                <p>Your enterprise resource planning dashboard. Manage customers, products, invoices and more.</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="number">1,254</div>
                    <div class="label">Customers</div>
                </div>
                <div class="stat">
                    <div class="number">458</div>
                    <div class="label">Products</div>
                </div>
                <div class="stat">
                    <div class="number">89</div>
                    <div class="label">Invoices</div>
                </div>
                <div class="stat">
                    <div class="number">$45.2K</div>
                    <div class="label">Revenue</div>
                </div>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>Quick Actions</h3>
                    <p>Create new invoices, add customers, or manage products.</p>
                    <a href="/admin/invoices.php">Create Invoice →</a>
                </div>
                <div class="card">
                    <h3>Recent Activity</h3>
                    <p>View recent orders, payments, and system logs.</p>
                    <a href="/admin/reports.php">View Reports →</a>
                </div>
                <div class="card">
                    <h3>System Tools</h3>
                    <p>Backup database, export data, and manage system settings.</p>
                    <a href="/admin/tools/">Admin Tools →</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
