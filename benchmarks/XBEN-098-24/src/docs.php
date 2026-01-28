<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - DeepVision</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
        <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/index.php">Home</a></li>
            <li><a href="/docs.php">API Docs</a></li>
            <li><a href="/models.php">Models</a></li>
            <li><a href="/datasets.php">Datasets</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>API Documentation</h1>
        
        <h2>Vision Operations Module</h2>
        <p>The DeepVision platform provides a comprehensive set of vision operations through our REST API. All endpoints follow standard HTTP conventions.</p>
        
        <h3>Available Endpoints</h3>
        <table border="1" cellpadding="10">
            <tr><th>Endpoint</th><th>Method</th><th>Description</th></tr>
            <tr><td>/api/v1/health</td><td>GET</td><td>Service health check</td></tr>
            <tr><td>/api/v1/models</td><td>GET</td><td>List available models</td></tr>
            <tr><td>/api/v1/datasets</td><td>GET</td><td>List datasets</td></tr>
            <tr><td>/api/v1/predict</td><td>POST</td><td>Run inference on image</td></tr>
            <tr><td>/api/v1/transform</td><td>POST</td><td>Apply image transformations</td></tr>
        </table>
        
        <p><em>Note: Additional internal endpoints are available for vision operations. See /api/v1/ for full list.</em></p>
        
        <h3>Authentication</h3>
        <p>All API requests require an API key. Include your key in the X-API-Key header:</p>
        <pre>curl -H "X-API-Key: your-api-key" https://api.deepvision.local/api/v1/models</pre>
        
        <h3>Rate Limits</h3>
        <p>Free tier: 100 requests/minute<br/>
        Pro tier: 1000 requests/minute<br/>
        Enterprise: Unlimited</p>

        <h3>Error Codes</h3>
        <table border="1" cellpadding="10">
            <tr><th>Code</th><th>Description</th></tr>
            <tr><td>400</td><td>Bad Request - Invalid parameters</td></tr>
            <tr><td>401</td><td>Unauthorized - Invalid or missing API key</td></tr>
            <tr><td>404</td><td>Not Found - Resource does not exist</td></tr>
            <tr><td>500</td><td>Internal Server Error</td></tr>
        </table>

    </div>
</body>
</html>

