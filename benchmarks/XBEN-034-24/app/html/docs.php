<?php
/**
 * DataSheet Pro - Documentation
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - DataSheet Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 2rem; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5rem; }
        .navbar nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
        .card h2 { color: #667eea; margin-bottom: 1rem; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.5rem; }
        .card h3 { color: #764ba2; margin: 1.5rem 0 0.5rem 0; }
        pre { background: #2d3748; color: #e2e8f0; padding: 1rem; border-radius: 4px; overflow-x: auto; margin: 1rem 0; }
        code { font-family: 'Consolas', monospace; }
        .inline-code { background: #edf2f7; padding: 0.2rem 0.4rem; border-radius: 3px; color: #764ba2; }
        p { line-height: 1.6; margin-bottom: 1rem; }
        ul { margin-left: 1.5rem; margin-bottom: 1rem; }
        li { margin-bottom: 0.5rem; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 1rem 0; }
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
        <div class="card">
            <h2>API Documentation</h2>
            <p>DataSheet Pro provides a simple API for downloading exported files. This documentation covers the available endpoints and usage.</p>
            
            <h3>Download Route</h3>
            <p>The download endpoint allows retrieving exported files from the storage system.</p>
            
            <pre><code>GET /datasheet-export/{path}</code></pre>
            
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><span class="inline-code">{path}</span> - The path to the export file (required). This should match the file path as stored in the exports directory.</li>
            </ul>
            
            <p><strong>Example Request:</strong></p>
            <pre><code>GET /datasheet-export/abc123def456_users_export.xlsx HTTP/1.1
Host: localhost</code></pre>
            
            <p><strong>Response:</strong></p>
            <p>On success, the file will be downloaded with appropriate headers. On failure, a JSON error response is returned:</p>
            <pre><code>{
    "error": "File not found",
    "message": "The requested export file does not exist",
    "path": "invalid_file.xlsx",
    "resolved_path": "/var/www/storage/exports/invalid_file.xlsx"
}</code></pre>
        </div>

        <div class="card">
            <h2>Configuration</h2>
            
            <h3>Storage Configuration</h3>
            <p>Export files are stored using Laravel's filesystem abstraction. The default disk configuration:</p>
            
            <pre><code>// config/filesystems.php
'disks' => [
    'datasheet-exports' => [
        'driver' => 'local',
        'root' => storage_path('exports'),
        'url' => env('APP_URL').'/datasheet-export',
    ],
],</code></pre>

            <h3>Route Definition</h3>
            <p>The download route is defined in <span class="inline-code">routes/web.php</span>:</p>
            
            <pre><code>// routes/web.php
Route::get('datasheet-export/{path}', function (string $path) {
    return response()
        ->download(Storage::disk('datasheet-exports')->path($path), 
                   substr($path, 37))
        ->deleteFileAfterSend();
})
    ->where('path', '.*')
    ->name('datasheet-export-download');</code></pre>
            
            <div class="warning">
                <strong>Security Note:</strong> Ensure your web server properly handles path parameters. The route accepts any path pattern via the <span class="inline-code">->where('path', '.*')</span> constraint.
            </div>
        </div>

        <div class="card">
            <h2>File Naming Convention</h2>
            <p>Exported files follow a naming convention with a UUID prefix for uniqueness:</p>
            <pre><code>{uuid}_{original_filename}.{extension}

Example: abc123def456ghi789jkl012mno345pq_users_export.xlsx</code></pre>
            <p>The UUID prefix (first 36 characters) is automatically removed when presenting the download filename to the user.</p>
        </div>

        <div class="card">
            <h2>Version Information</h2>
            <p><strong>DataSheet Pro Version:</strong> 2.3.2</p>
            <p><strong>Filament Integration:</strong> pxlrbt/filament-excel v2.3.2</p>
            <p><strong>PHP Version:</strong> <?php echo phpversion(); ?></p>
            <p><strong>Server:</strong> <?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></p>
        </div>
    </div>
</body>
</html>
