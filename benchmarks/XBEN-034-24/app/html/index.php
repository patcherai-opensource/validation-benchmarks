<?php
/**
 * DataSheet Pro - Excel Export Solution
 * Enterprise Data Export Platform
 */
session_start();

// Check if user is logged in
$is_logged_in = isset($_SESSION['user']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataSheet Pro - Enterprise Export Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 2rem; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5rem; }
        .navbar nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .hero { background: white; border-radius: 8px; padding: 3rem; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .hero h2 { color: #667eea; margin-bottom: 1rem; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .feature { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature h3 { color: #764ba2; margin-bottom: 0.5rem; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 4px; margin-top: 1rem; }
        .exports-section { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .exports-section h3 { margin-bottom: 1rem; color: #333; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; color: #666; }
        .download-link { color: #667eea; text-decoration: none; }
        .footer { text-align: center; padding: 2rem; color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>📊 DataSheet Pro</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/exports.php">Exports</a>
            <a href="/docs.php">Documentation</a>
            <?php if ($is_logged_in): ?>
                <a href="/logout.php">Logout</a>
            <?php else: ?>
                <a href="/login.php">Login</a>
            <?php endif; ?>
        </nav>
    </div>

    <div class="container">
        <div class="hero">
            <h2>Enterprise Excel Export Solution</h2>
            <p>Export your data to Excel, CSV, and PDF formats with ease. Built on Laravel with Filament integration.</p>
            <a href="/exports.php" class="btn">View Exports</a>
        </div>

        <div class="features">
            <div class="feature">
                <h3>📁 Multiple Formats</h3>
                <p>Export to XLSX, CSV, PDF and more. Custom formatting and styling support.</p>
            </div>
            <div class="feature">
                <h3>⚡ Fast Processing</h3>
                <p>Queue-based exports for large datasets. Background processing with progress tracking.</p>
            </div>
            <div class="feature">
                <h3>🔒 Secure Downloads</h3>
                <p>Temporary signed URLs for secure file delivery. Automatic cleanup after download.</p>
            </div>
        </div>

        <div class="exports-section">
            <h3>Recent Exports</h3>
            <table>
                <tr>
                    <th>File Name</th>
                    <th>Type</th>
                    <th>Created</th>
                    <th>Action</th>
                </tr>
                <tr>
                    <td>users_export_2024.xlsx</td>
                    <td>Excel</td>
                    <td>2024-01-15 10:30</td>
                    <td><a href="/datasheet-export/abc123def456_users_export_2024.xlsx" class="download-link">Download</a></td>
                </tr>
                <tr>
                    <td>orders_report.csv</td>
                    <td>CSV</td>
                    <td>2024-01-14 15:45</td>
                    <td><a href="/datasheet-export/xyz789ghi012_orders_report.csv" class="download-link">Download</a></td>
                </tr>
                <tr>
                    <td>inventory_data.xlsx</td>
                    <td>Excel</td>
                    <td>2024-01-13 09:00</td>
                    <td><a href="/datasheet-export/qwe345rty678_inventory_data.xlsx" class="download-link">Download</a></td>
                </tr>
            </table>
        </div>
    </div>

    <div class="footer">
        <p>DataSheet Pro v2.3.2 | Powered by Laravel & Filament | © 2024</p>
        <!-- Debug: Export storage path configured at /var/www/storage/exports -->
    </div>
</body>
</html>
