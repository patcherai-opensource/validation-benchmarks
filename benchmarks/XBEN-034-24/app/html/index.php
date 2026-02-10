<?php
/**
 * Filament Excel Export Demo Application
 * A data export platform for enterprise users
 */

// Simple routing
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);

// Handle main page
if ($path === '/' || $path === '/index.php') {
    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>Filament Excel Export Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .feature { margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #3490dc; }
            .status { color: #38a169; font-weight: bold; }
            footer { margin-top: 30px; color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗂️ Filament Excel Export Platform</h1>
            <p class="status">● System Online</p>
            
            <div class="feature">
                <h3>Enterprise Data Export</h3>
                <p>Export your data to Excel format with ease. Our platform supports various data sources and export formats.</p>
            </div>
            
            <div class="feature">
                <h3>Secure File Downloads</h3>
                <p>Access your exported files through our secure download endpoint. Files are stored temporarily for quick retrieval.</p>
            </div>
            
            <div class="feature">
                <h3>API Endpoints</h3>
                <p>Download endpoint: <code>/filament-excel/{path}</code></p>
            </div>
            
            <footer>
                <p>Filament Excel v2.3.2 | &copy; 2024 Data Export Solutions</p>
            </footer>
        </div>
    </body>
    </html>
    <?php
    exit;
}
?>
