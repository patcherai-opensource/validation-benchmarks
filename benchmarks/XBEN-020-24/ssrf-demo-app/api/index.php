<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GeoPortal API Documentation</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c5530; }
        h2 { color: #3a6b3e; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .endpoint { background: #e8f5e9; padding: 15px; border-left: 4px solid #2c5530; margin: 15px 0; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-weight: bold; margin-right: 10px; }
        .get { background: #4caf50; }
        .post { background: #2196f3; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 GeoPortal API v2.1</h1>
        <p>Welcome to the GeoPortal REST API documentation. This API provides access to geographic data, layers, maps, and proxy services.</p>
        
        <h2>Authentication</h2>
        <p>Most endpoints require API key authentication. Include your API key in the <code>X-Api-Key</code> header.</p>
        <p>Public endpoints (marked with 🔓) do not require authentication.</p>
        
        <h2>Endpoints</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/layers</code>
            <p>Returns a list of available map layers.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/maps</code>
            <p>Returns a list of saved maps.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/documents</code>
            <p>Returns a list of uploaded documents.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span><code>/proxy/</code> 🔓
            <p>Proxy endpoint for fetching external WMS/WFS resources. Used for accessing external tile servers and geo-services.</p>
            <table>
                <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
                <tr><td><code>url</code></td><td>string</td><td>The URL to proxy (must be from an allowed host)</td></tr>
            </table>
            <p><strong>Example:</strong></p>
            <pre>GET /proxy/?url=https://wms.openstreetmap.org/cgi-bin/wms</pre>
            <p><strong>Note:</strong> Only requests to whitelisted geo-service domains are permitted for security reasons.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/capabilities</code>
            <p>Returns server capabilities and supported operations.</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span><code>/api/upload</code>
            <p>Upload a new geospatial dataset. Requires admin privileges.</p>
        </div>
        
        <h2>Rate Limits</h2>
        <p>API requests are limited to 1000 requests per hour per API key. The proxy endpoint has additional restrictions on target hosts.</p>
        
        <h2>Errors</h2>
        <table>
            <tr><th>Code</th><th>Description</th></tr>
            <tr><td>400</td><td>Bad Request - Invalid parameters</td></tr>
            <tr><td>401</td><td>Unauthorized - Invalid or missing API key</td></tr>
            <tr><td>403</td><td>Forbidden - Access denied (e.g., host not allowed for proxy)</td></tr>
            <tr><td>404</td><td>Not Found - Resource does not exist</td></tr>
            <tr><td>502</td><td>Bad Gateway - Proxy request failed</td></tr>
        </table>
    </div>
</body>
</html>
