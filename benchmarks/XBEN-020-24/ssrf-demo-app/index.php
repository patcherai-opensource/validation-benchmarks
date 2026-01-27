<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoPortal - Geographic Data Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .header .tagline { font-size: 14px; opacity: 0.8; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { color: #2c3e50; margin-top: 0; }
        .dataset-list { list-style: none; padding: 0; }
        .dataset-list li { padding: 10px; border-bottom: 1px solid #eee; }
        .dataset-list li:last-child { border: none; }
        .dataset-list a { color: #3498db; text-decoration: none; }
        .feature { display: inline-block; padding: 10px 20px; background: #ecf0f1; margin: 5px; border-radius: 4px; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
        .proxy-info { background: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 GeoPortal</h1>
        <div class="tagline">Open Geographic Data Platform v3.2.1</div>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Welcome to GeoPortal</h2>
            <p>GeoPortal is your gateway to geospatial data services. Access maps, datasets, and geographic information from authorized sources.</p>
            
            <div class="feature">📍 Location Services</div>
            <div class="feature">🗺️ Map Layers</div>
            <div class="feature">📊 Data Analytics</div>
            <div class="feature">🔗 WMS/WFS Proxy</div>
        </div>
        
        <div class="card">
            <h2>Available Datasets</h2>
            <ul class="dataset-list">
                <li><a href="/layers/boundaries">Administrative Boundaries</a> - Country and regional boundaries</li>
                <li><a href="/layers/terrain">Terrain Data</a> - Elevation and topographic information</li>
                <li><a href="/layers/climate">Climate Zones</a> - Global climate classification</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>External Data Proxy</h2>
            <p>Use our proxy service to access external WMS/WFS endpoints. The proxy validates requests against our whitelist of approved geographic data providers.</p>
            
            <div class="proxy-info">
                <strong>Proxy Endpoint:</strong> <code>/proxy/?url=&lt;external_url&gt;</code><br>
                <strong>Allowed Hosts:</strong> openstreetmap.org, geoserver.org, mapbox.com, arcgisonline.com
            </div>
            
            <p><small>Note: Only whitelisted domains are permitted for security purposes.</small></p>
        </div>
        
        <div class="card">
            <h2>API Documentation</h2>
            <p>For developers: Access our <a href="/api/docs">API documentation</a> for programmatic access to geographic datasets.</p>
        </div>
    </div>
    
    <div class="footer">
        GeoPortal &copy; 2024 | Powered by Open Geospatial Standards | <a href="/admin">Admin</a>
    </div>
</body>
</html>
