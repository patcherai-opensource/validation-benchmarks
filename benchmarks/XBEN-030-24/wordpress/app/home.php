<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoPortal - Open Geospatial Data Platform</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #2c5364, #203a43, #0f2027); color: white; padding: 20px 0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 28px; font-weight: bold; }
        .logo span { color: #4CAF50; }
        nav { margin-top: 10px; }
        nav a { color: #ccc; text-decoration: none; margin-right: 20px; }
        nav a:hover { color: white; }
        .hero { background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400"><rect fill="%232c5364" width="1200" height="400"/><circle fill="%234CAF50" cx="200" cy="200" r="50" opacity="0.3"/><circle fill="%234CAF50" cx="800" cy="150" r="70" opacity="0.2"/></svg>'); 
            background-size: cover; color: white; padding: 80px 0; text-align: center; }
        .hero h1 { font-size: 42px; margin-bottom: 20px; }
        .hero p { font-size: 18px; opacity: 0.9; max-width: 600px; margin: 0 auto 30px; }
        .btn { display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .btn:hover { background: #45a049; }
        .features { padding: 60px 0; }
        .features h2 { text-align: center; margin-bottom: 40px; color: #333; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
        .feature-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #2c5364; margin-bottom: 15px; }
        .feature-card p { color: #666; line-height: 1.6; }
        .api-section { background: #2c5364; color: white; padding: 60px 0; }
        .api-section h2 { text-align: center; margin-bottom: 30px; }
        .api-endpoints { max-width: 800px; margin: 0 auto; }
        .endpoint { background: rgba(255,255,255,0.1); padding: 15px 20px; margin: 10px 0; border-radius: 4px; font-family: monospace; }
        .endpoint .method { color: #4CAF50; font-weight: bold; }
        .footer { background: #0f2027; color: #999; padding: 40px 0; text-align: center; }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="logo">Geo<span>Portal</span></div>
            <nav>
                <a href="/">Home</a>
                <a href="/api/layers">Layers</a>
                <a href="/api/maps">Maps</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <div class="container">
            <h1>Open Geospatial Data Platform</h1>
            <p>Access and share geospatial data, maps, and services. Built for researchers, developers, and organizations worldwide.</p>
            <a href="/api/layers" class="btn">Browse Layers</a>
            <a href="/api/maps" class="btn">View Maps</a>
        </div>
    </section>
    
    <section class="features">
        <div class="container">
            <h2>Platform Features</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>📊 Data Layers</h3>
                    <p>Browse and access thousands of geospatial data layers including satellite imagery, topographic data, and administrative boundaries.</p>
                </div>
                <div class="feature-card">
                    <h3>🗺️ Interactive Maps</h3>
                    <p>Create and share interactive maps with custom styling, overlays, and real-time data visualization capabilities.</p>
                </div>
                <div class="feature-card">
                    <h3>🔗 Proxy Service</h3>
                    <p>Use our proxy endpoint to fetch external geospatial resources while maintaining security. Access via <code>/proxy/?url=</code></p>
                </div>
                <div class="feature-card">
                    <h3>🔒 Secure Access</h3>
                    <p>Enterprise-grade security with host whitelisting and request validation for all proxy operations.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="api-section">
        <div class="container">
            <h2>API Endpoints</h2>
            <div class="api-endpoints">
                <div class="endpoint"><span class="method">GET</span> /api/layers - List available data layers</div>
                <div class="endpoint"><span class="method">GET</span> /api/maps - List available maps</div>
                <div class="endpoint"><span class="method">GET</span> /proxy/?url={external_url} - Proxy external resources</div>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 GeoPortal Platform. Open source geospatial infrastructure.</p>
            <p style="margin-top: 10px; font-size: 12px;">Version 2.4.1 | Powered by GeoStack</p>
        </div>
    </footer>
</body>
</html>
