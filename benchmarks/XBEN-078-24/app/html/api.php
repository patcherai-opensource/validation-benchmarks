<?php
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - GlobalCMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>GlobalCMS API Documentation</h1>
    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/content.php">Content Library</a>
        <a href="/api.php" class="active">API Documentation</a>
        <a href="/admin/">Admin Panel</a>
    </nav>
    
    <div class="api-docs">
        <h2>REST API Reference</h2>
        <p>The GlobalCMS API allows programmatic access to content and translation management features.</p>
        
        <div class="api-section">
            <h3>Authentication</h3>
            <p>All admin API endpoints require authentication via session cookies. Authenticate by POSTing to <code>/admin/</code> with username and password.</p>
        </div>
        
        <div class="api-section">
            <h3>Content API</h3>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/content.php?category={category}</code>
                <p>Retrieve content items filtered by category.</p>
            </div>
        </div>
        
        <div class="api-section">
            <h3>Translation API</h3>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/admin/translations.php</code>
                <p>Query translation strings with JSON filters.</p>
                <div class="code-block">
                    <h4>Request Body</h4>
                    <pre>{
  "filter": [
    {
      "property": "locale",
      "type": "string", 
      "value": "en_US"
    },
    {
      "property": "key",
      "type": "string",
      "value": "welcome",
      "operator": "like"
    }
  ]
}</pre>
                </div>
                <div class="code-block">
                    <h4>Response</h4>
                    <pre>{
  "success": true,
  "count": 2,
  "data": [
    {"id": 1, "key": "welcome_message", "locale": "en_US", "translation": "Welcome!"},
    {"id": 2, "key": "welcome_back", "locale": "en_US", "translation": "Welcome back!"}
  ]
}</pre>
                </div>
            </div>
        </div>
        
        <div class="api-section">
            <h3>Error Responses</h3>
            <p>API errors return JSON with error details:</p>
            <pre>{
  "error": "Query failed",
  "message": "Error description"
}</pre>
        </div>
    </div>
</div>
<footer>
    <p>&copy; 2024 GlobalCMS - Version 4.2.1</p>
</footer>
</body>
</html>
