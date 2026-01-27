<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - DataAnnotate</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <script src="/static/js/app.js"></script>
</head>
<body>
    <header class="header">
        <h1>DataAnnotate</h1>
        <nav class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/projects.php">Projects</a>
            <a href="/docs.php">Documentation</a>
            <a href="/login.php">Sign In</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="card">
            <h2>Documentation</h2>
            <p>Welcome to the DataAnnotate documentation. Learn how to set up and use the platform.</p>
        </div>
        
        <div class="card">
            <h3>Installation</h3>
            <p>DataAnnotate can be deployed using Docker or installed directly on your server.</p>
            <pre style="background: #f1f5f9; padding: 15px; border-radius: 5px;">
# Docker deployment
docker pull dataannotate/dataannotate:latest
docker run -p 8080:80 dataannotate/dataannotate

# Configuration files are located in:
# /var/www/app/core/settings/settings.py
            </pre>
        </div>
        
        <div class="card">
            <h3>Configuration</h3>
            <p>The platform is configured through environment variables and configuration files:</p>
            <ul>
                <li><strong>SECRET_KEY</strong> - Django secret key for session security</li>
                <li><strong>DATABASE_URL</strong> - PostgreSQL connection string</li>
                <li><strong>REDIS_URL</strong> - Redis connection for caching and task queue</li>
                <li><strong>ML_BACKEND_URL</strong> - URL for ML-assisted labeling backend</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>Static Files</h3>
            <p>Static assets (CSS, JavaScript, images) are served from the <code>/static</code> endpoint.</p>
            <p>Example: <code>/static/css/main.css</code>, <code>/static/js/app.js</code></p>
        </div>
        
        <div class="card">
            <h3>API Reference</h3>
            <h4>Authentication</h4>
            <pre style="background: #f1f5f9; padding: 15px; border-radius: 5px;">
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "your_password"
}
            </pre>
            
            <h4>Projects API</h4>
            <pre style="background: #f1f5f9; padding: 15px; border-radius: 5px;">
# List projects
GET /api/projects

# Create project
POST /api/projects
{
    "name": "My Project",
    "description": "Image classification project"
}

# Export annotations
GET /api/projects/{id}/export?format=COCO
            </pre>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2024 DataAnnotate Platform v2.1.0</p>
    </footer>
</body>
</html>
