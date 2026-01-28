<?php
// API Documentation for SolarView Dashboard
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>SolarView | API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; color: #f7931a !important; }
        .bg-solar { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; }
        code { color: #e83e8c; }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header Section -->
    <header class="py-5 bg-solar text-white border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">API Reference</h1>
                <p class="lead">SolarView Dashboard REST API v1.34.2</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Available Endpoints</h5>
                    </div>
                    <div class="card-body">
                        <h6><code>GET /index.php</code></h6>
                        <p>Returns the main dashboard with available widgets.</p>
                        
                        <hr>
                        
                        <h6><code>GET /widget.php?id={widget_id}</code></h6>
                        <p>Retrieves details for a specific widget.</p>
                        <p><strong>Parameters:</strong></p>
                        <ul>
                            <li><code>id</code> - Widget identifier (e.g., "data-viz", "analytics")</li>
                        </ul>
                        
                        <hr>
                        
                        <h6><code>GET /cdn.php?path={asset_path}</code></h6>
                        <p>Retrieves cached static assets from the CDN.</p>
                        <p><strong>Parameters:</strong></p>
                        <ul>
                            <li><code>path</code> - Relative path to the cached asset</li>
                        </ul>
                        <p><strong>Example:</strong></p>
                        <pre>GET /cdn.php?path=widget-styles.css</pre>
                        
                        <hr>
                        
                        <h6><code>GET /static/{path}</code></h6>
                        <p>Direct access to static resources.</p>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Response Formats</h5>
                    </div>
                    <div class="card-body">
                        <p>All API responses are returned in their native format (HTML, JSON, CSS, etc.).</p>
                        <p>Error responses are returned as JSON:</p>
                        <pre>{
    "error": "Asset not found",
    "path": "requested/path",
    "cache_dir": "/var/www/html/static/cache/"
}</pre>
                    </div>
                </div>
            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
