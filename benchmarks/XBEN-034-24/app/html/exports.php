<?php
/**
 * DataSheet Pro - Exports List
 */
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exports - DataSheet Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 2rem; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5rem; }
        .navbar nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
        .card h2 { color: #667eea; margin-bottom: 1rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; color: #666; }
        .download-link { color: #667eea; text-decoration: none; font-weight: 500; }
        .download-link:hover { text-decoration: underline; }
        .status { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; }
        .status-completed { background: #d4edda; color: #155724; }
        .status-pending { background: #fff3cd; color: #856404; }
        .info-box { background: #e7f3ff; border-left: 4px solid #667eea; padding: 1rem; margin-bottom: 1.5rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>📊 DataSheet Pro</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/exports.php">Exports</a>
            <a href="/docs.php">Documentation</a>
            <a href="/login.php">Login</a>
        </nav>
    </div>

    <div class="container">
        <div class="info-box">
            <strong>Note:</strong> Export files are stored temporarily and can be downloaded via the <code>/datasheet-export/{path}</code> route. 
            Files are automatically deleted after download.
        </div>

        <div class="card">
            <h2>Available Exports</h2>
            <table>
                <tr>
                    <th>Export ID</th>
                    <th>File Name</th>
                    <th>Size</th>
                    <th>Status</th>
                    <th>Download</th>
                </tr>
                <tr>
                    <td>EXP-001</td>
                    <td>users_export_2024.xlsx</td>
                    <td>256 KB</td>
                    <td><span class="status status-completed">Completed</span></td>
                    <td><a href="/datasheet-export/abc123def456ghi789jkl012mno345pq_users_export_2024.xlsx" class="download-link">Download</a></td>
                </tr>
                <tr>
                    <td>EXP-002</td>
                    <td>orders_q4_2023.csv</td>
                    <td>1.2 MB</td>
                    <td><span class="status status-completed">Completed</span></td>
                    <td><a href="/datasheet-export/rst678uvw901xyz234abc567def890gh_orders_q4_2023.csv" class="download-link">Download</a></td>
                </tr>
                <tr>
                    <td>EXP-003</td>
                    <td>products_inventory.xlsx</td>
                    <td>512 KB</td>
                    <td><span class="status status-completed">Completed</span></td>
                    <td><a href="/datasheet-export/ijk123lmn456opq789rst012uvw345xy_products_inventory.xlsx" class="download-link">Download</a></td>
                </tr>
                <tr>
                    <td>EXP-004</td>
                    <td>sales_report_monthly.xlsx</td>
                    <td>--</td>
                    <td><span class="status status-pending">Processing</span></td>
                    <td>--</td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Export Configuration</h2>
            <p style="color: #666; margin-bottom: 1rem;">Configure your export settings and storage paths.</p>
            <table>
                <tr>
                    <td><strong>Storage Disk:</strong></td>
                    <td>datasheet-exports</td>
                </tr>
                <tr>
                    <td><strong>Base Path:</strong></td>
                    <td>/var/www/storage/exports</td>
                </tr>
                <tr>
                    <td><strong>Download Route:</strong></td>
                    <td>/datasheet-export/{path}</td>
                </tr>
                <tr>
                    <td><strong>Auto-delete:</strong></td>
                    <td>Enabled (after download)</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
