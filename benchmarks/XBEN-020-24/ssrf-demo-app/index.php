<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoPortal - Geographic Data Services</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #2c5530 0%, #1a3a1f 100%); color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #3a6b3e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .footer { background: #333; color: #aaa; padding: 20px; text-align: center; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 GeoPortal</h1>
        <p>Geographic Data Services Platform v3.4.2</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/layers/">Layers</a>
        <a href="/maps/">Maps</a>
        <a href="/documents/">Documents</a>
        <a href="/api/">API</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to GeoPortal</h2>
            <p>GeoPortal is a platform for managing and sharing geospatial data, maps, and applications. 
            Our platform enables organizations to create, discover, and use geographic information.</p>
        </div>
        <div class="card">
            <h2>Featured Layers</h2>
            <ul>
                <li>Global Administrative Boundaries</li>
                <li>OpenStreetMap Base Layer</li>
                <li>Satellite Imagery (2023)</li>
                <li>Elevation Data (DEM)</li>
            </ul>
        </div>
        <div class="card">
            <h2>Quick Links</h2>
            <ul>
                <li><a href="/api/">API Documentation</a></li>
                <li><a href="/layers/">Browse All Layers</a></li>
                <li><a href="/maps/">View Maps</a></li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>GeoPortal &copy; 2024 | Powered by Open Source GIS Technologies</p>
    </div>
</body>
</html>
