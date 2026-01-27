<?php
// PyDash Documentation
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyDash - Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .sidebar { position: sticky; top: 20px; }
        .code-block { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; }
        pre code { font-family: 'Courier New', monospace; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><strong>PyDash</strong> <small class="text-muted">v2.3.1</small></a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/docs.php">Documentation</a></li>
                    <li class="nav-item"><a class="nav-link" href="/examples.php">Examples</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <div class="row">
            <div class="col-md-3">
                <div class="sidebar">
                    <h5>Documentation</h5>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link" href="#getting-started">Getting Started</a></li>
                        <li class="nav-item"><a class="nav-link" href="#components">Components</a></li>
                        <li class="nav-item"><a class="nav-link" href="#static-files">Static Files</a></li>
                        <li class="nav-item"><a class="nav-link" href="#cdn-api">CDN API</a></li>
                    </ul>
                </div>
            </div>
            <div class="col-md-9">
                <h1>PyDash Documentation</h1>
                <p class="lead">Learn how to build interactive dashboards with PyDash.</p>
                
                <section id="getting-started" class="mt-5">
                    <h2>Getting Started</h2>
                    <p>Install PyDash using pip:</p>
                    <div class="code-block"><pre><code>pip install pydash-framework</code></pre></div>
                </section>
                
                <section id="components" class="mt-5">
                    <h2>Components</h2>
                    <p>PyDash uses a component-based architecture similar to React.</p>
                    <div class="code-block">
<pre><code>from pydash import Component

@app.component
def MyComponent(props):
    return Component("div", [
        Component("h1", props.title),
        Component("p", props.content)
    ])</code></pre>
                    </div>
                </section>
                
                <section id="static-files" class="mt-5">
                    <h2>Static File Serving</h2>
                    <p>PyDash serves static files from multiple locations:</p>
                    <ul>
                        <li><code>/static/public/</code> - Public assets accessible to all users</li>
                        <li><code>/static/assets/</code> - Application-specific assets</li>
                        <li><code>/_pydash/cdn/</code> - Cached CDN resources</li>
                    </ul>
                    <div class="alert alert-info">
                        <strong>Note:</strong> Static files are served with caching headers for optimal performance.
                    </div>
                </section>
                
                <section id="cdn-api" class="mt-5">
                    <h2>CDN API</h2>
                    <p>The CDN endpoint caches and serves external libraries locally:</p>
                    <div class="code-block">
<pre><code># Request a cached asset
GET /_pydash/cdn/pydash.min.js

# Alternative endpoint format
GET /_pydash/cdn.php/pydash.min.js

# Response headers
Content-Type: application/javascript
X-CDN-Cache: HIT
X-Served-By: pydash-cdn/2.3.1</code></pre>
                    </div>
                    <p class="mt-3">Assets are cached in the <code>/static/cdn/</code> directory and served with appropriate MIME types.</p>
                    
                    <div class="alert alert-secondary mt-3">
                        <strong>Security Note:</strong> Path traversal sequences like <code>../</code> are filtered from requests for security. 
                        File paths are URL-decoded after security filtering to support special characters in filenames.
                    </div>
                </section>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-3 mt-5">
        <div class="container text-center">
            <small>PyDash Framework v2.3.1</small>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
