<?php
// PyDash - Python Dashboard Framework
// Version 2.3.1 - Interactive Data Visualization Platform
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyDash - Interactive Dashboard Framework</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
        }
        .feature-card {
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .code-block {
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
        }
        .navbar-brand img {
            height: 40px;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <strong>PyDash</strong> <small class="text-muted">v2.3.1</small>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link active" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/docs.php">Documentation</a></li>
                    <li class="nav-item"><a class="nav-link" href="/examples.php">Examples</a></li>
                    <li class="nav-item"><a class="nav-link" href="/static/public/readme.txt">Static Files</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 fw-bold">Build Interactive Dashboards with Python</h1>
            <p class="lead mt-3">PyDash is a modern framework for creating reactive web applications and data visualizations using pure Python.</p>
            <div class="mt-4">
                <a href="/docs.php" class="btn btn-light btn-lg me-2">Get Started</a>
                <a href="/examples.php" class="btn btn-outline-light btn-lg">View Examples</a>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">Key Features</h2>
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <h4>🔄 Reactive Components</h4>
                            <p>Build reactive UIs that update automatically when your data changes.</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <h4>📊 Data Visualization</h4>
                            <p>Integrate with popular charting libraries like Plotly, Bokeh, and Matplotlib.</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <h4>🚀 Fast Development</h4>
                            <p>Hot reload support for rapid iteration during development.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Quick Start Section -->
    <section class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">Quick Start</h2>
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="code-block">
                        <pre><code># Install PyDash
pip install pydash-framework

# Create your first dashboard
from pydash import Dashboard, Component

app = Dashboard()

@app.component
def HelloWorld():
    return Component("h1", "Hello, PyDash!")

app.run()</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- API Info Section -->
    <section class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">Static Asset Serving</h2>
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h5>CDN Endpoints</h5>
                            <p>PyDash serves static assets through multiple endpoints:</p>
                            <ul>
                                <li><code>/_pydash/cdn/&lt;path&gt;</code> - CDN cached assets</li>
                                <li><code>/static/public/&lt;path&gt;</code> - Public static files</li>
                                <li><code>/static/assets/&lt;path&gt;</code> - Application assets</li>
                            </ul>
                            <!-- Note: Static paths are resolved relative to the assets directory -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p class="mb-0">PyDash Framework v2.3.1 | Built with Python</p>
            <small class="text-muted">© 2024 PyDash Contributors</small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
