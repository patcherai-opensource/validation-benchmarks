<?php
// PyDash Examples
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyDash - Examples</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .example-card { transition: transform 0.2s; }
        .example-card:hover { transform: scale(1.02); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><strong>PyDash</strong> <small class="text-muted">v2.3.1</small></a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/docs.php">Documentation</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/examples.php">Examples</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <h1 class="text-center mb-5">Example Dashboards</h1>
        
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card example-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📊 Sales Dashboard</h5>
                        <p class="card-text">Real-time sales metrics with interactive charts and filters.</p>
                        <span class="badge bg-primary">Analytics</span>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card example-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🌡️ IoT Monitor</h5>
                        <p class="card-text">Monitor temperature and humidity sensors across multiple locations.</p>
                        <span class="badge bg-success">IoT</span>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card example-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📈 Stock Tracker</h5>
                        <p class="card-text">Track stock prices with candlestick charts and technical indicators.</p>
                        <span class="badge bg-warning">Finance</span>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card example-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🔬 Data Explorer</h5>
                        <p class="card-text">Upload and visualize datasets with automatic chart suggestions.</p>
                        <span class="badge bg-info">Data Science</span>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card example-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🎮 Game Stats</h5>
                        <p class="card-text">Gaming statistics dashboard with player rankings and match history.</p>
                        <span class="badge bg-danger">Gaming</span>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card example-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🌍 Geo Heatmap</h5>
                        <p class="card-text">Visualize geographic data with interactive heatmaps.</p>
                        <span class="badge bg-secondary">Geospatial</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-5 text-center">
            <p class="text-muted">More examples coming soon. Check the <a href="/docs.php">documentation</a> to build your own!</p>
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
