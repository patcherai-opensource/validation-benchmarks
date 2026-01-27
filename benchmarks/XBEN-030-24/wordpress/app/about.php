<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - GeoPortal</title>
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
        .content { padding: 60px 0; }
        .content h1 { color: #2c5364; margin-bottom: 30px; }
        .content p { color: #666; line-height: 1.8; margin-bottom: 20px; }
        .tech-stack { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-top: 30px; }
        .tech-stack h2 { color: #2c5364; margin-bottom: 20px; }
        .tech-stack ul { list-style: none; }
        .tech-stack li { padding: 10px 0; border-bottom: 1px solid #eee; }
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
    
    <section class="content">
        <div class="container">
            <h1>About GeoPortal</h1>
            <p>GeoPortal is an open-source geospatial data platform designed to facilitate the sharing and visualization of geographic information. Our platform enables researchers, developers, and organizations to access, analyze, and share geospatial data seamlessly.</p>
            
            <p>The platform provides a comprehensive suite of tools including data layer management, interactive mapping capabilities, and a secure proxy service for accessing external geospatial resources.</p>
            
            <div class="tech-stack">
                <h2>Technical Information</h2>
                <ul>
                    <li><strong>Version:</strong> 2.4.1</li>
                    <li><strong>Backend:</strong> PHP 8.1</li>
                    <li><strong>Proxy Service:</strong> cURL with host whitelisting</li>
                    <li><strong>Supported Protocols:</strong> HTTP, HTTPS, WMS, WFS, WCS</li>
                    <li><strong>Internal Services:</strong> Metadata service on port 8081 (localhost only)</li>
                </ul>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 GeoPortal Platform. Open source geospatial infrastructure.</p>
        </div>
    </footer>
</body>
</html>
